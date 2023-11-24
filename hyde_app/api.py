import frappe
from datetime import datetime, timedelta
from hrms.hr.doctype.job_applicant.job_applicant import get_interview_details

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
def get_job_applicant_id(applicant_name):
    job_applicant_id = frappe.get_value("Job Applicant", {"applicant_name": applicant_name}, "name")
    return job_applicant_id

@frappe.whitelist()
def get_annexure_template_details(template):
	introduction = frappe.get_list(
		"Annexure Template",
		fields=["introduction"],
		filters={"name": template},
	)[0]
     
	annexure_details = frappe.get_all(
		"Annexure Child Table",
		fields=["component", "amount"],
		filters={"parent": template},
		order_by="idx"
	)
	return introduction,annexure_details


@frappe.whitelist()
def Interview_Rounds(job_titles):
    source_data = frappe.db.sql("""SELECT interview_rounds FROM `tabInterview Rounds` WHERE parent = '{0}' ORDER BY idx """.format(job_titles),as_dict=True)
    return source_data

@frappe.whitelist()
def get_user_details(user):
    user_list = frappe.get_list(
		"User",
          fields=["full_name","name"],
		filters = {
               "name":user
        }
	)
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
def get_interviewers_list(interview):
    # Define the filters to get interview details for a specific interview
    filters = {
        "parent": interview, # Filter by the name of the parent interview document
        "parenttype": "Interview",  # Filter by the parenttype
    }

    # Use frappe.get_list to retrieve interview details with the specified filters
    interview_details = frappe.get_list(
        "Interview Detail",
        fields=["interviewer"],  # You can specify the fields you want to retrieve
        filters=filters,
    )
    interviewers_list = [item["interviewer"] for item in interview_details]
    change_interview_status(interview,interview_details)
    return interview_details



def change_interview_status(interview_id,interviewer_list):
    try:
        feedback_docs = frappe.get_all("Interview Feedback",filters={"interview":interview_id})
        statuses = []
        for i in feedback_docs:
            feedback_doc = frappe.get_doc("Interview Feedback",i["name"])
            statuses.append(feedback_doc.result)
        if len(statuses)==len(interviewer_list):
            interview_doc = frappe.get_doc("Interview",interview_id)
            status = set(statuses)
            status = sorted(status)
            if len(status)>1:
                interview_doc.status = "Under Review"
                interview_doc.save(ignore_permissions=True)
                frappe.db.commit()
            elif len(status)==1:
                interview_doc.status = status[0]
                interview_doc.save(ignore_permissions=True)
                frappe.db.commit()

        else:
            interview_doc = frappe.get_doc("Interview",interview_id)
            interview_doc.status = "Under Review"
            interview_doc.save(ignore_permissions=True)
            frappe.db.commit()
    except Exception as e:
        print(f"Error occured : {e}")

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

@frappe.whitelist()
def send_appointment_email(doc, method):
    applicant_data = frappe.get_value(
       "Job Applicant",
       {"name": doc.job_applicant},
       ["email_id", "job_title", "applicant_name"],
       as_dict=True
   )
    applicant_email = applicant_data.get("email_id")
    applicant_name = applicant_data.get("applicant_name")
    position = applicant_data.get("job_title")

   # Email content for the candidate
    email_content_candidate = f"""\
       <p>Dear {applicant_name},</p>
       <p>Greetings of the day!</p>
       <p>Heartiest congratulations! We are pleased to offer you the position of {position} with Korecent Solutions Pvt. Ltd.</p>
       <p>Below enclosed is your appointment letter. Please let us know incase of any assistance.</p>
       <p>Welcome aboard !</p>
       <p>Thanks and regards,</p>
       <p>HR- Team KoreCent</p>
   """
   # Email content for the interviewer
    email_content_interviewer = f"""\
       <p>Dear Interviewer,</p>
       <p>Greetings! We have sent the appointment letter to the candidate, {applicant_name} ({applicant_email}), for the position of {position} with Korecent Solutions Pvt. Ltd.</p>
       <p>If you have any additional feedback or instructions, please feel free to share.</p>
       <p>Thanks and regards,</p>
       <p>HR- Team KoreCent</p>
   """
   # Send email to the candidate
    frappe.sendmail(
       recipients=applicant_email,
       cc=frappe.get_doc('HR Manager Settings').hr_email_id,
       subject='Job Offer Notification',
       message=email_content_candidate,
       attachments=[{"file_url": doc.custom_appointment_letter}],
       now=True
   )
   # Send email to the interviewer
    frappe.sendmail(
       recipients=[doc.custom_interviewer_email],
       subject='Candidate Status Update',
       message=email_content_interviewer,
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

            table_rows = ""
            for name, interview_data in feedback['interviews'].items():
                interviewers_list = frappe.get_list(
                    "Interview Detail",
                    filters={"parent": name, "parenttype": "Interview"},
                    pluck="custom_interviewer_name"
                )
                table_rows += f"""
                    <tr>
                        <td style="padding:5px;">{interview_data['interview_round']}</td>
                        <td style="padding:5px;">{interview_data['status']}</td>
                        <td style="padding:5px;">{interview_data['average_rating']}</td>
                        <td style="padding:5px;">{", ".join(interviewers_list)}</td>
                    </tr>
                """

            message = f'''\
                <p>Dear HR Team,</p>
                <p>Greetings! We would like to inform you that the job applicant, {doc.custom_job_applicant_name}, has successfully cleared all interview process for the position of {doc.job_opening} with Korecent Solutions Pvt. Ltd.</p>
                <p>Below enclosed are his interview round wise results:</p>
                <table border="1">
                    <thead>
                        <tr>
                            <th style="padding:5px;">Interview Round</th>
                            <th style="padding:5px;">Status</th>
                            <th style="padding:5px;">Average Rating</th>
                            <th style="padding:5px;">Interviewer Name</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
                <p>Please proceed with the necessary steps.<p>
                <p>Thanks and regards,</p>
                <p>Automated Notification System</p>
            '''
            frappe.sendmail(
                recipients=[recipient_email],
                subject=subject,
                message=message,
                now=True,
          )
    if (
        doc.status == "Rejected"
        and not doc.custom_rejection_email_sent
    ):
        applicant_data = frappe.get_value(
            "Job Applicant",
            {"name": doc.job_applicant},
            ["email_id", "job_title", "applicant_name"],
            as_dict=True
            )
        applicant_email = applicant_data.get("email_id")
        applicant_name = applicant_data.get("applicant_name")
        subject ="Your Application Status with KoreCent Solutions Pvt Ltd."
        email_content_after_interview_rejection = (
            f"<p>Dear {applicant_name},</p>"
            "<p>Greetings of the day!</p>"
            "<p>Thank you for completing the interview process with KoreCent Solutions Pvt Ltd. We acknowledge your commendable background and appreciate the opportunity to learn more about you.</p>"
            "<p>Unfortunately, we will not be moving forward with your application at this time as our current requirements do not align with your skills.</p>"
            "<p>We have your details in our database and will reach out to you in case a suitable opening arises in our organization.</p>"
            "<p>Wishing you all the very best.</p>"
            "<p>Thanks and regards,<br>HR - Team KoreCent</p>"
)
        frappe.sendmail(
        recipients=applicant_email,
        subject=subject,
        message=email_content_after_interview_rejection,
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


        message = f"""
        <br>
        Dear {employee_name},
        <br>
        <br>
        
        Greetings of the day!
        <br>
        <br>

        Your compensatory leave request has been approved for the From Date: {work_from_date} To End Date: {work_end_date}. Balance of the same has been added to your leaves.
        <br>
        <br>
        <br>

        Thanks and regards,
        <br>
        HR-Team KoreCent
        """

        frappe.sendmail(
            recipients=employee_email,
            subject="Compensatory Leave Request Notification",
            message=message,
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
def get_interviewer_details(job_applicant):
    interview_details = frappe.db.get_all(
        "Interview",
        filters={"job_applicant": job_applicant, "docstatus": ["!=", 2]},
        fields=["name"],
    )

    interviewer_details_list = []
    for interview in interview_details:
        filters = {
            "parent": interview["name"],
            "parenttype": "Interview",
        }
        interviewer_details = frappe.get_list(
            "Interview Detail",
            fields=["interviewer", "custom_interviewer_name"],
            filters=filters,
        )
        interview["interviewer_details"] = interviewer_details
        interviewer_details_list.append(interview)

    return interviewer_details_list


@frappe.whitelist()
def send_job_applicant_creation_email(doc,method):
    job_applicant_creation= f"""\
        Dear HR,<br><br>
        Greetings of the day!<br><br>
        We want to inform you that a new job application has been submitted for the { doc.job_title } .<br>
        The name of the candidate is { doc.applicant_name } and his resume has been attached for your reference along with the website link : {"https://kcs-ess.frappe.cloud/" }<br><br>
        Kindly do the needful.<br>
        Thanks and regards <br>
        HR- Team KoreCent
        """
    frappe.sendmail(
        recipients=frappe.get_doc('HR Manager Settings').hr_email_id,
        subject='New job Applicant created notification',
        message=job_applicant_creation,
        attachments=[{"file_url": doc.resume_attachment}],
        now=True
    )
    subject = f"Job application received for {doc.job_title} with KoreCent Solutions Pvt Ltd."
    email_content_for_successful_application = (
        f"<p>Dear {doc.applicant_name},</p>"
        "<p>Greetings of the day!</p>"
        "<p>Thank you for your interest in KoreCent Solutions Pvt Ltd. We have received your application "
        f"for {doc.job_title}. Currently, we are reviewing your application and will get back to you "
        "in case you are selected for further hiring processes.</p>"
        "<p>Wishing you all the very best.</p>"
        "<p>Thanks and regards,<br></p>"
        "<p>HR - Team KoreCent</p>"
    )
    frappe.sendmail(
        recipients=doc.email_id,
        subject=subject,
        message=email_content_for_successful_application,
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

def send_email_to_applicant(doc):
    subject = f"Job application received for {doc.job_title} with KoreCent Solutions Pvt Ltd."
    email_content_for_rejection_application = (
    f"<p>Dear {doc.applicant_name},</p>"
    "<p>Greetings of the day!</p>"
    f"<p>Thank you for your interest in KoreCent Solutions Pvt Ltd. We have received your application for {doc.job_title}. "
    "Upon carefully reviewing your application, it is evident that your skills at the time and our requirements are not in line. We express our gratitude to you for considering KoreCent Solutions, and wish you good luck ahead.</p>"
    "<p>We have your details in our database and will get back to you in case we have a suitable opening in our organization.</p>"
    "<p>Wishing you all the very best.</p>"
    "<p>Thanks and regards,<br>HR - Team KoreCent</p>"
)

    frappe.sendmail(
        recipients=doc.email_id,
        subject=subject,
        message=email_content_for_rejection_application,
        now=True
    )


@frappe.whitelist()
def send_email_on_interview_scheduled(doc,method):
    try:
        # getting attachments from job applocant--------------------
        attachments ,applicant_name= frappe.db.get_value('Job Applicant', {'name': doc.job_applicant}, ['resume_attachment','applicant_name'])
        # sending email on creation of interview to interviewer-------------------
        email_interviewer = f"""\
            <p>Dear {doc.interview_details[0].custom_interviewer_name}, </p>
            
            <p>Greetings of the day! </p>
            
            <p>An interview has been scheduled for {doc.designation} on {doc.scheduled_on} at {doc.from_time}. Candidate name is {doc.custom_job_applicant_name}.</p> <p>It will be a { doc.interview_round }.</p>
            
            <p>Below enclosed is the resume for your reference </a>.</p>
            {f"<p>Interview Link: {doc.custom_interview_link}</p>" if doc.custom_interview_type == "Online" else f"<p>Address: {doc.custom_address}</p>"}
            
            <p>Please ensure your availability for the interview, and in case of any rescheduling, let us know 1 day in advance.</p>
            
            <div style='padding: 20px; text-align: center;'>
            <p style='font-size: 18px; margin-bottom: 20px;'>We value your feedback!</p>
            <a href='https://kcs-ess.frappe.cloud/app/interview-feedback/view/list?interview={doc.name}' 
            style='background-color: #007BFF; color: #fff; text-decoration: none; display: inline-block; padding: 15px 30px; border-radius: 5px; font-size: 16px;'>
            Provide Feedback
            </a>
            </div>
            
            <p>Thanks and regards</p>
            <p>HR- Team KoreCent</p>
        """
        
        # sending email on creation of interview to job applicant-------------------
        
        job_applicant_email=f"""\
            <p>Dear { applicant_name },</p>

            <p>Greetings of the day!</p>

            <p>We are pleased to inform you that your interview has been scheduled for { doc.designation } on { doc.scheduled_on } at { doc.from_time }.</p><p>It will be a { doc.interview_round }.</p>
            {f"<p>Interview Link: {doc.custom_interview_link}</p>" if doc.custom_interview_type == "Online" else f"<p>Address: {doc.custom_address}</p>"}

            <p>Wishing you the best for your interview.</p>

            <p>Thanks and regards,</p>
            <p>HR-Team KoreCent</p>"""

        frappe.sendmail(
            recipients=doc.interview_details[0].interviewer,
            cc=frappe.get_doc('HR Manager Settings').hr_email_id,
            subject=f"Interview of {applicant_name} for {doc.designation} on {doc.scheduled_on}",
            message=email_interviewer,
            attachments=[{"file_url": attachments if attachments else ""}],
            now=True
        )
        
        
        frappe.sendmail(
            recipients=doc.job_applicant,
            cc=frappe.get_doc('HR Manager Settings').hr_email_id,
            subject=f"Interview for {doc.designation} with KoreCent Solutions Pvt. Ltd  on {doc.scheduled_on}.",
            message=job_applicant_email,
            now=True
        )
        
    except:
        pass


def send_reminder_email(applicant_email, subject, message):
    frappe.sendmail(
        recipients=applicant_email,
        cc=frappe.get_doc('HR Manager Settings').hr_email_id,
        subject=subject,
        message=message,
        now=True
    )

def get_rejected_job_offers_created(days_ago, closing=False):
    today = datetime.now().date()
    target_date = today - timedelta(days=days_ago)
    start_time = datetime.combine(target_date, datetime.min.time())
    end_time = datetime.combine(target_date, datetime.max.time())
    filters = [
        ["creation", ">", start_time],
        ["creation", "<", end_time],
        ["status", "=", "Awaiting Response"]
    ]

    rejected_job_offers = frappe.get_all("Job Offer", filters=filters)

    for job_offer in rejected_job_offers:
        doc = frappe.get_doc("Job Offer", job_offer.name)
        applicant_data = frappe.get_value(
            "Job Applicant",
            {"name": doc.job_applicant},
            [ "job_title"],
            as_dict=True
            )
        position = applicant_data.get("job_title")

        if not closing:
            subject = f"Job offer {position} with KoreCent Solutions Pvt Ltd."
            message = f"""\
        <p>Dear {doc.applicant_name},</p>
        <p>Greetings of the day!</p>
        <p>Heartiest congratulations! We are pleased to offer you the position of {position} with Korecent Solutions Pvt. Ltd. at {doc.custom_ctc} CTC.</p>
        <p>Please take the necessary action on the below enclosed link within the next 7 days:</p>
        <p>Below enclosed is your detailed job offer pdf.</p>
        <a href="{frappe.utils.get_url()}/api/method/hyde_app.api.accept_offer?name={doc.name}" onclick="this.style.pointerEvents = 'none'; this.style.background = '#ccc';" style="background-color: #4CAF50; color: #fff; padding: 10px 20px; text-decoration: none; display: inline-block; border-radius: 5px; margin-right: 10px;">Accept</a>
        <a href="{frappe.utils.get_url()}/api/method/hyde_app.api.reject_offer?name={doc.name}" onclick="this.style.pointerEvents = 'none'; this.style.background = '#ccc';" style="background-color: #FF5733; color: #fff; padding: 10px 20px; text-decoration: none; display: inline-block; border-radius: 5px;">Reject</a>
        <p>Thanks and regards,</p>
        <p>HR- Team KoreCent</p>
        """
            
        else:
            subject = "Closing of Job Opening"
            message = (
                f"<p>Dear {doc.applicant_name},</p>"
                "<p>Thank you for your completing the interview process KoreCent Solutions Pvt ltd. You have a commendable background and we appreciate you giving us the opportunity to learn more about you. Unfortunately since you have not taken any necessary action after releasing your  job offer, unfortunately we will not be moving forward with your application.</p>"
                "<p>We encourage you to continue to review our careers site and apply for the positions that interests you.</p>"
                "<p>Wishing you all the very best.<br>Thanks and regards,<br>HR- Team KoreCent</p>"
            )
        send_reminder_email(doc.applicant_email, subject, message)

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
    interview_feedback_records = frappe.get_list(
        "Interview Feedback",
        filters={"interview": interview_name},
        fields=["name"],
    )
    # Fetch each record separately using get_doc
    feedback_docs = []
    for record in interview_feedback_records:
        feedback_doc = frappe.get_doc("Interview Feedback", record.name)
        feedback_docs.append(feedback_doc)

    return feedback_docs

# =========================  code for sending mail from job offer to its accept or reject state ======================== >>

def get_applicant_data(applicant_name):
    applicant_data = frappe.get_value("Job Applicant",filters={"name": applicant_name},fieldname=["email_id", "job_title", "applicant_name"],as_dict=True)
    return (applicant_data.get("email_id"),applicant_data.get("applicant_name"),applicant_data.get("job_title"))

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

@frappe.whitelist(allow_guest=True)
def accept_offer(name):
    """
    Handles the process when a candidate accepts a job offer.
    Retrieves the job offer document, updates its status to 'Accepted',
    sends an acceptance email to the candidate, and generates a response page.
    """
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

@frappe.whitelist(allow_guest=True)
def reject_offer(name):
    """
    Manages the process when a candidate rejects a job offer.
    Retrieves the job offer document, updates its status to 'Rejected',
    sends a rejection email to the candidate and HR, and generates a response page.
    """
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


# <============================= Start of Functions to prepare email content =============================>

def prepare_email_content_job_offer(applicant_name, position, ctc, doc_name):
    return f"""\
        <p>Dear {applicant_name},</p>
        <p>Greetings of the day!</p>
        <p>Heartiest congratulations! We are pleased to offer you the position of {position} with Korecent Solutions Pvt. Ltd. at {ctc} CTC.</p>
        <p>Please take the necessary action on the below enclosed link within the next 7 days:</p>
        <p>Below enclosed is your detailed job offer pdf.</p>
        <a href="{frappe.utils.get_url()}/api/method/hyde_app.api.accept_offer?name={doc_name}" onclick="this.style.pointerEvents = 'none'; this.style.background = '#ccc';" style="background-color: #4CAF50; color: #fff; padding: 10px 20px; text-decoration: none; display: inline-block; border-radius: 5px; margin-right: 10px;">Accept</a>
        <a href="{frappe.utils.get_url()}/api/method/hyde_app.api.reject_offer?name={doc_name}" onclick="this.style.pointerEvents = 'none'; this.style.background = '#ccc';" style="background-color: #FF5733; color: #fff; padding: 10px 20px; text-decoration: none; display: inline-block; border-radius: 5px;">Reject</a>
        <p>Thanks and regards,</p>
        <p>HR- Team KoreCent</p>
        """ 

def prepare_email_content_job_offer_hr(position,applicant_name):
    released_by = frappe.session.user  
    user_fullname = frappe.get_value("User", released_by, "username")
    return f"""\
        <p>Dear {frappe.get_doc('HR Manager Settings').hr_manager_name}</p>
        <p>This is to inform you that the job offer for the position of {position} to {applicant_name} has been released.</p>
        <p>The offer was extended by: {user_fullname} ({released_by})</p>
        <p>Kindly take note of this action in your records.</p><br><br>
        <p>Auto-generated mail.</p>
        <p>Thank you.</p>
        """ 

def handle_already_accepted_or_rejected(status):
    if status == "Accepted":
        return frappe.respond_as_web_page("Offer Already Accepted", "<h1>The offer has already been accepted.</h1>")
    elif status == "Rejected":
        return frappe.respond_as_web_page("Offer Already Rejected", "<h1>The offer has already been rejected.</h1>")

def prepare_response_page(title, message):
    page_content = f"""
    
            <h1>{message}</h1>
       
        """
    return frappe.respond_as_web_page(title, page_content)

def prepare_acceptance_email(job_position,job_offer):
    return  f"""
        <p>Dear {job_offer.applicant_name},</p>
        <p>Greetings of the day!</p>
        <p>Heartiest congratulations! We are pleased to have you with Korecent Solutions Pvt. Ltd. as a {job_position}.</p>
        <p>The tentative start date will be {job_offer.custom_tentative_start_date}. Please let us know in case you have another date of joining at the earliest so that we can start with the further process accordingly.</p>
        <p>Some of these details would need to be verified; you are requested to submit scanned copies of the documents mentioned below within 3 days of this offer or your joining, whichever is earlier:</p>
        <ul>
            <li>Copy of graduation/post-graduation certificate</li>
            <li>Govt. photo ID card (e.g., Adhar Card)</li>
            <li>PAN number</li>
            <li>Relieving/Experience letter from your previous organization (when you receive it)</li>
            <li>Last drawn salary slip</li>
            <li>Scan of the latest passport size photo</li>
            <li>Emergency contact numbers</li>
            <li>Permanent residence address and correspondence (if different from the current)</li>
        </ul>
        <p>Also, as discussed, we have a "bring your own device" policy.</p>
        <p>We look forward to welcoming you to our team and working together to achieve great things.</p>
        <p>Thanks and regards,</p>
        <p>HR- Team KoreCent</p>
        """

def prepare_rejection_email(applicant_name):
    return f"""
        <p>Dear {applicant_name},</p>
        <p>Greetings of the day!</p>
        <p>We are sorry to know that you have decided to decline the job offer. We want to reach out in order to address your concerns and feedback. Kindly let us know your availability so that we can plan a call accordingly.</p>
        <p>Thanks and regards,</p>
        <p>HR- Team KoreCent</p>
        """
def prepare_rejection_email_hr(applicant_name,job_applicant,job_position):
    return f"""
        <p>Dear {frappe.get_doc('HR Manager Settings').hr_manager_name},</p>
        <p>Greetings of the day!</p>
        <p>We want to inform you that the {applicant_name}({job_applicant}) who was offered the {job_position} position with Korecent Solutions Pvt. Ltd has rejected the job offer. An email has been sent to them seeking their availability to address their concerns.</p>
        <p>Kindly plan to connect with them accordingly.</p>
        <p>Thanks and regards,</p>
        <p>HR- Team KoreCent</p>
        """
# <============================= End of Functions to prepare email content =============================>
# ========================= End code for sending mail from job offer to its accept or reject state ======================== >>
