import frappe
from hrms.hr.doctype.job_applicant.job_applicant import get_interview_details
from hyde_app.notifications import (
    prepare_email_content_job_offer,
    prepare_email_content_job_offer_hr,
    handle_already_accepted_or_rejected,
    prepare_acceptance_email,
    prepare_rejection_email,
    prepare_rejection_email_hr,
    email_content_candidate,
    email_content_interviewer,
    email_content_after_interview_rejection,
    email_content__compensatory_leave_request,
    email_content_for_successful_application,
    job_applicant_creation_hr,
    send_email_to_applicant,
    prepare_email_content_on_interview_scheduled,
    prepare_email_content_on_interview_scheduled_to_applicat,
    get_rejected_job_offers_created,
    content_for_hr_all_rounds_cleared)

@frappe.whitelist()
def update_applicant_status_interview(applicant_name, status):
    # This function Written for five Js Functions(ap_letter.js, employee_onboarding.js, employee.js, interview.js, job_offer.js,)
    try:
        applicant = frappe.get_doc("Job Applicant", applicant_name)
        applicant.status = status
        applicant.save()
        applicant.reload()
        frappe.db.commit()
    except frappe.DoesNotExistError:
        frappe.msgprint(f"Job Applicant '{applicant_name}' not found.")

@frappe.whitelist()
def get_annexure_template_details(template):
	introduction = frappe.get_list("Annexure Template",fields=["introduction"],filters={"name": template},)[0]
	annexure_details = frappe.get_all("Annexure Child Table",fields=["component", "amount"],filters={"parent": template},order_by="idx")
	return introduction,annexure_details


@frappe.whitelist()
def Interview_Rounds(job_titles):
    source_data = frappe.db.sql("""SELECT interview_rounds FROM `tabInterview Rounds` WHERE parent = '{0}' ORDER BY idx """.format(job_titles),as_dict=True)
    return source_data

@frappe.whitelist()
def get_user_details(user):
    user_list = frappe.get_list("User",fields=["full_name","name"],filters = { "name":user })
    return user_list

@frappe.whitelist()
def get_job_applicant_details(job_applicant,job_opening):
    values = {'name':job_opening}
    source_data = frappe.db.sql("""SELECT  ir.interview_rounds FROM `tabJob Opening` jo JOIN `tabInterview Rounds` ir ON jo.name = ir.parent WHERE     jo.name = %(name)s ORDER BY ir.idx""",values = values,as_dict=True   )

    job_applicant_details = frappe.get_list(
		"Interview",
          fields=["interview_round","job_applicant","job_opening","status"],
		filters = {
               "job_applicant":job_applicant,
               "job_opening":job_opening
        }
	)
    return job_applicant_details,source_data


@frappe.whitelist()
def get_interviewers_list(interview,result):
    sql = """
        SELECT
            di.interviewer
        FROM
            `tabInterview` i
        INNER JOIN
            `tabInterview Detail` di ON i.name = di.parent
        WHERE
            i.name = %s
    """
    interviewr_details = frappe.db.sql(sql, (interview,), as_dict=False)
    interview_doc = frappe.get_doc("Interview",interview)
    for interviewer in interviewr_details:
        status = frappe.db.get_list('Interview Feedback',filters={'interview': interview,"interviewer":interviewer[0]},fields=['result'],as_list=True)
        if not status:
            interview_doc.status = "Under Review"
            interview_doc.save(ignore_permissions=True)
            interview_doc.reload()
            frappe.db.commit()
            return
        for i in status:
            if i[0] != result:
                interview_doc.status = "Under Review"
                interview_doc.save(ignore_permissions=True)
                interview_doc.reload()
                frappe.db.commit()
                return
    interview_doc.status =result
    interview_doc.save(ignore_permissions=True)
    interview_doc.reload()
    frappe.db.commit()
    return        

@frappe.whitelist(allow_guest=True)
def get_job_applications(email):
    job_applications = frappe.get_all(
       'Job Applicant',
    filters={
           'email_id': email
       },
    fields=['name', 'job_title', 'status', 'applicant_name', 'applicant_rating']
        )
    for application in job_applications:
        application['interview_summary'] = get_interview_details(application['name'])
    return job_applications

def get_applicant_data(applicant_name):
    applicant_data = frappe.get_value("Job Applicant",filters={"name": applicant_name},fieldname=["email_id", "job_title", "applicant_name"],as_dict=True)
    return (applicant_data.get("email_id"),applicant_data.get("applicant_name"),applicant_data.get("job_title"))

@frappe.whitelist()
def send_appointment_email(doc, method):
    applicant_email, applicant_name, position = get_applicant_data(doc.job_applicant)
   # Send email to the candidate
    frappe.sendmail(
       recipients=applicant_email,
       cc=frappe.get_doc('HR Manager Settings').hr_email_id,
       subject='Job Offer Notification',
       message=email_content_candidate(applicant_name,position),
       attachments=[{"file_url": doc.custom_appointment_letter}],
       now=True
   )
   # Send email to the interviewer
    frappe.sendmail(
       recipients=[doc.custom_interviewer_email],
       subject='Candidate Status Update',
       message=email_content_interviewer(applicant_name,applicant_email,position),
       now=True
   )

@frappe.whitelist()
def get_latest_interview(job_applicant):
    sql = """
        SELECT
            di.interviewer
        FROM
            `tabInterview` i
        INNER JOIN
            `tabInterview Detail` di ON i.name = di.parent
        WHERE
            i.job_applicant = %s
        ORDER BY
            i.creation DESC, di.idx DESC
        LIMIT 1
    """
    interviewer = frappe.db.sql(sql, (job_applicant,), as_dict=False)
    return interviewer[0][0] if interviewer else None

@frappe.whitelist()
def notify_hr_on_interview_update(doc, method):
    feedback = get_interview_details(doc.job_applicant)
    if  doc.status =='Cleared':
        job_opening = frappe.get_doc("Job Opening", doc.job_opening)
        all_rounds_cleared = True
        for i in job_opening.custom_round:
            sql_query = f"""
              SELECT
                  *
              FROM
                  `tabInterview`
              WHERE
                  `job_applicant` = %s
                  AND `interview_round` = %s
              ORDER BY
                  `creation` DESC
              LIMIT 1
          """
            interview_record = frappe.db.sql(sql_query, (doc.job_applicant, i.interview_rounds), as_dict=True)
            if interview_record:
                if interview_record[0].status != "Cleared":
                    all_rounds_cleared = False
            else:
                all_rounds_cleared = False

        if all_rounds_cleared:
            recipient_email = frappe.get_doc('HR Manager Settings').hr_email_id
            subject = 'Completion of the interview process'

            frappe.sendmail(
                recipients=[recipient_email],
                subject=subject,
                message=content_for_hr_all_rounds_cleared(feedback,doc),
                now=True,
          )
    if (
        doc.status == "Rejected"
        and not doc.custom_rejection_email_sent
    ):
        applicant_email, applicant_name, position = get_applicant_data(doc.job_applicant)
        subject ="Your Application Status with KoreCent Solutions Pvt Ltd."

        frappe.sendmail(
        recipients=applicant_email,
        subject=subject,
        message=email_content_after_interview_rejection(applicant_name),
        now=True
        )

        doc.custom_rejection_email_sent = 1
        doc.save(ignore_permissions=True) 

@frappe.whitelist()
def send_compensatory_leave_request(doc, method):
    if doc.workflow_state == "Approved":
        employee_id = doc.employee
        if not employee_id:
            frappe.throw("Employee ID is missing")

        work_from_date = doc.work_from_date
        work_end_date = doc.work_end_date
        doc = frappe.get_doc("Employee", employee_id)
        employee_email = doc.company_email
        employee_name = doc.employee_name

        frappe.sendmail(
            recipients=employee_email,
            subject="Compensatory Leave Request Notification",
            message=email_content__compensatory_leave_request(employee_name,work_from_date,work_end_date),
            header="Compensatory Leave Request Notification"
        )

@frappe.whitelist()
def get_job_opening_rounds(job_title):
    return frappe.get_doc("Job Opening",job_title)

@frappe.whitelist()
def get_latest_interview_date(job_applicant):
    values = {'name': job_applicant}
    data = frappe.db.sql("""
       SELECT scheduled_on
       FROM `tabInterview`
       WHERE job_applicant = %(name)s
       ORDER BY scheduled_on DESC limit 1
   """, values=values, as_dict=0)
    if data:
       return data[0][0]
    else:
        return None
    
@frappe.whitelist()
def get_latest_job_offer_date(job_applicant):
    values = {'name': job_applicant}
    data = frappe.db.sql("""
       SELECT offer_date
       FROM `tabJob Offer`
       WHERE job_applicant = %(name)s
       ORDER BY offer_date DESC limit 1
   """, values=values, as_dict=0)
    if data:
        return data[0][0]
    else:
       return None



@frappe.whitelist()
def create_or_check_contact(email, mobile, name):
    contact =frappe.db.exists({"doctype": "Contact", "email_id":email})
    if contact:
        return 'exists' 
    else:
        new_contact = frappe.get_doc({
            "doctype": "Contact",
            "first_name": name,
            "email_ids": [{"email_id":email,"is_primary":1}],
                        "phone_nos": [{"phone":mobile,"is_primary":1}],
        })
        new_contact.insert()
        frappe.db.commit()
        return 'created' 
    

@frappe.whitelist()
def send_job_applicant_creation_email(doc,method):
    frappe.sendmail(
        recipients=frappe.get_doc('HR Manager Settings').hr_email_id,
        subject='New job Applicant created notification',
        message=job_applicant_creation_hr(doc.job_title, doc.applicant_name ),
        attachments=[{"file_url": doc.resume_attachment}],
        now=True
    )
    subject = f"Job application received for {doc.job_title} with KoreCent Solutions Pvt Ltd."
    frappe.sendmail(
        recipients=doc.email_id,
        subject=subject,
        message=email_content_for_successful_application(doc.applicant_name,doc.job_title),
        now=True
    )

@frappe.whitelist()
def send_rejection_email_to_job_applicant_if_not_sent(doc, method):
    if (
        doc.status == "Rejected"
        and not doc.custom_rejection_email_sent
    ):
        send_email_to_applicant(doc)
        doc.custom_rejection_email_sent = 1
        doc.save(ignore_permissions=True)

@frappe.whitelist()
def send_email_on_interview_scheduled(doc,method):
    try:
        # getting attachments from job applocant--------------------
        attachments ,applicant_name= frappe.db.get_value('Job Applicant', {'name': doc.job_applicant}, ['resume_attachment','applicant_name'])
        frappe.sendmail(
            recipients=doc.interview_details[0].interviewer,
            cc=frappe.get_doc('HR Manager Settings').hr_email_id,
            subject=f"Interview of {applicant_name} for {doc.designation} on {doc.scheduled_on}",
            message=prepare_email_content_on_interview_scheduled(doc),
            attachments=[{"file_url": attachments if attachments else ""}],
            now=True
        )
        
        frappe.sendmail(
            recipients=doc.job_applicant,
            cc=frappe.get_doc('HR Manager Settings').hr_email_id,
            subject=f"Interview for {doc.designation} with KoreCent Solutions Pvt. Ltd  on {doc.scheduled_on}.",
            message=prepare_email_content_on_interview_scheduled_to_applicat(applicant_name,doc),
            now=True
        ) 
    except:
        pass

@frappe.whitelist(allow_guest=True)
def execute_job_offer_workflow():
    get_rejected_job_offers_created(2)
    get_rejected_job_offers_created(5)
    get_rejected_job_offers_created(7, closing=True)


@frappe.whitelist(allow_guest=True)
def restrict_to_create_job_offer(job_applicant_email,job_applicant_id):
    job_applicant_details = frappe.get_list(
            "Job Applicant",
            fields=["job_title"],
            filters = {
                "email_id":job_applicant_email,               
            }
        )
    job_interview_details = frappe.get_list(
            "Interview",
            fields=["interview_round","status"],
            filters = {
                "job_applicant":job_applicant_id    
            }
        )
    
    candidate_interview_rounds = [entry['interview_round'] for entry in job_interview_details]
    unique_candidate_interview_rounds = set(candidate_interview_rounds)
    unique_candidate_interview_rounds = sorted(unique_candidate_interview_rounds)
    job_title = job_applicant_details[0].job_title

    values = {'name':job_title}
    source_data = frappe.db.sql("""SELECT  ir.interview_rounds FROM `tabJob Opening` jo JOIN `tabInterview Rounds` ir ON jo.name = ir.parent WHERE     jo.name = %(name)s ORDER BY ir.idx""",values = values,as_dict=True   )
    
    job_interview_rounds = [entry['interview_rounds'] for entry in source_data]
    unique_job_interview_rounds = set(job_interview_rounds)
    unique_job_interview_rounds = sorted(unique_job_interview_rounds)

    rounds_check = len(unique_candidate_interview_rounds) == len(unique_job_interview_rounds)
    
    return 1 if rounds_check else 0, job_interview_details

@frappe.whitelist()
def get_interview_feedback(interview_name):
    # Fetch records for the specific interview with child table data
    interview_feedback_records = frappe.get_list("Interview Feedback",filters={"interview": interview_name},fields=["name"],)
    # Fetch each record separately using get_doc
    feedback_docs = []
    for record in interview_feedback_records:
        feedback_doc = frappe.get_doc("Interview Feedback", record.name)
        feedback_docs.append(feedback_doc)

    return feedback_docs

# =========================  code for sending mail from job offer to its accept or reject state ======================== >>

@frappe.whitelist()
def send_Job_offer_email(doc, method):
    applicant_email, applicant_name, position = get_applicant_data(doc.job_applicant)
    # Send job offer notification to applicant and HR in CC
    frappe.sendmail(recipients=applicant_email,
                       subject='Job Offer Notification', 
                       message=prepare_email_content_job_offer(applicant_name, position, doc.custom_ctc, doc.name),
                       attachments=[{"file_url": doc.custom_offer_letter}],
                       cc=frappe.get_doc('HR Manager Settings').hr_email_id,
                       now=True)

    #email for HR notification about the job offer release
    frappe.sendmail(recipients=frappe.get_doc('HR Manager Settings').hr_email_id,
                      subject='Job Offer Released to Applicant - Action Update',
                      message=prepare_email_content_job_offer_hr(position,applicant_name),
                      now=True)
    
#triggered when a candidate accepts a job offer & sends an acceptance email to the candidate, and generates a response page.
@frappe.whitelist(allow_guest=True)
def accept_offer(name):
    job_offer = frappe.get_doc("Job Offer", name)
    if job_offer.status in ("Accepted", "Rejected"):
        return handle_already_accepted_or_rejected(job_offer.status)

    job_offer.status = "Accepted"
    job_offer.save(ignore_permissions=True)
    frappe.db.commit()

    applicant_email, applicant_name, position = get_applicant_data(job_offer.job_applicant)
    # Send acceptance email to the candidate and HR in CC
    frappe.sendmail(recipients=applicant_email,
                      subject='Job Offer Accepted',
                      message=prepare_acceptance_email(position,job_offer),
                      cc=frappe.get_doc('HR Manager Settings').hr_email_id,
                      now=True)
    return frappe.respond_as_web_page("Offer Accepted", "<h1>Thanks for accepting the offer!</h1><p>You will receive the Appointment letter soon.</p>")

#Triggred when a candidate rejects a job offer ,sends a rejection email to the candidate and HR, and generates a response page.
@frappe.whitelist(allow_guest=True)
def reject_offer(name):
    job_offer = frappe.get_doc("Job Offer", name)
    if job_offer.status in ("Accepted", "Rejected"):
        return handle_already_accepted_or_rejected(job_offer.status)
    
    job_offer.status = "Rejected"
    job_offer.save(ignore_permissions=True)
    frappe.db.commit()

    applicant_email, applicant_name, position = get_applicant_data(job_offer.job_applicant)
    # Send rejection email to the candidate and HR
    frappe.sendmail(
      recipients=applicant_email,
      cc=frappe.get_doc('HR Manager Settings').hr_email_id,
      subject='Job Offer Rejected',
      message=prepare_rejection_email(job_offer.applicant_name),
      now = True
    )
    frappe.sendmail(
      recipients=applicant_email,
      cc=frappe.get_doc('HR Manager Settings').hr_email_id,
      subject='Job Offer Rejected',
      message=prepare_rejection_email_hr(job_offer.applicant_name,job_offer.job_applicant,position),
      now = True
    )
    return frappe.respond_as_web_page("Offer Rejected", "<h1>Offer Rejected</h1> <p>Thank you for considering our offer. If you change your mind, please feel free to contact us.</p>")

# ========================= End code for sending mail from job offer to its accept or reject state ======================== >>
