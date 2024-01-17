import frappe
import json
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
    content_for_hr_all_rounds_cleared,
    email_content_candidate_for_changing_interview_mode,
    email_content_interviewer_for_changing_interview_mode)
from frappe.utils import cstr, flt, get_datetime, get_link_to_form, getdate, nowtime, add_days, formatdate
import json

@frappe.whitelist()
def get_total_score(email_id):
    total_score = 0
    total_questions = 0
    lms_quiz = frappe.get_all("LMS Quiz Submission",
                              filters={"member": email_id})
    for submission in lms_quiz:
        filter_value = submission.name
        quiz_submission = frappe.get_doc("LMS Quiz Submission", filter_value)
        total_score = total_score+int(quiz_submission.score)
        total_questions = total_questions+len(quiz_submission.result)
    return {"total_score": total_score, "total_questions": total_questions}


def set_average_rating(self):
    total_rating = 0
    for entry in self.interview_details:
        if entry.average_rating:
            total_rating += entry.average_rating

    average_rating_val = flt(
        total_rating /
        len(self.interview_details) if len(self.interview_details) else 0
    )

    average_rating_val = average_rating_val * 10
    rounded_value = round(average_rating_val)
    if rounded_value % 2 != 0:
        rounded_value += 1
    print(rounded_value / 10)
    self.average_rating = rounded_value / 10


@frappe.whitelist()
def update_applicant_status_interview(applicant_name, status):
    add_status_option_to_job_applicant(status)
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
    introduction = frappe.get_list("Annexure Template", fields=[
                                   "introduction"], filters={"name": template},)[0]
    annexure_details = frappe.get_all("Annexure Child Table", fields=[
                                      "component", "amount"], filters={"parent": template}, order_by="idx")
    return introduction, annexure_details


@frappe.whitelist()
def Interview_Rounds(job_titles):
    source_data = frappe.db.sql(
        """SELECT interview_rounds FROM `tabInterview Rounds` WHERE parent = '{0}' ORDER BY idx """.format(job_titles), as_dict=True)
    return source_data


@frappe.whitelist()
def get_user_details(user):
    user_list = frappe.get_list(
        "User", fields=["full_name", "name"], filters={"name": user})
    return user_list


@frappe.whitelist()
def get_job_applicant_details(job_applicant, job_opening):
    values = {'name': job_opening}
    source_data = frappe.db.sql(
        """SELECT  ir.interview_rounds FROM `tabJob Opening` jo JOIN `tabInterview Rounds` ir ON jo.name = ir.parent WHERE     jo.name = %(name)s ORDER BY ir.idx""", values=values, as_dict=True)

    job_applicant_details = frappe.get_list(
        "Interview",
        fields=["interview_round", "job_applicant", "job_opening", "status"],
        filters={
            "job_applicant": job_applicant,
            "job_opening": job_opening
        }
    )
    return job_applicant_details, source_data

@frappe.whitelist()
def add_status_option_to_job_applicant(interview_round):
    property_setter = frappe.get_doc("Property Setter", "Job Applicant-status-options")
    current_options = property_setter.value.split("\n")    
    if interview_round not in current_options:
        current_options.append(interview_round)
        property_setter.value = "\n".join(option for option in current_options)
        property_setter.save()
        frappe.clear_cache()

@frappe.whitelist()
def get_interviewers_list(interview, result):
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
    interview_doc = frappe.get_doc("Interview", interview)
    applicant_id = interview_doc.job_applicant
    interview_round=interview_doc.interview_round
    status_options=frappe.get_meta("Job Applicant").get_field("status").options.split("\n")
    for interviewer in interviewr_details:
        status = frappe.db.get_list('Interview Feedback', filters={
                                    'interview': interview, "interviewer": interviewer[0]}, fields=['result'], as_list=True)
        if not status:
            interview_doc.status = "Under Review"
            interview_doc.save(ignore_permissions=True)
            interview_doc.reload()
            frappe.db.commit()
            update_applicant_status_interview(
                applicant_id, "Interview Scheduled")
            return
        for i in status:
            if i[0] != result:
                interview_doc.status = "Under Review"
                interview_doc.save(ignore_permissions=True)
                interview_doc.reload()
                frappe.db.commit()
                update_applicant_status_interview(
                    applicant_id, "Interview Scheduled")
                return

    if result == "Cleared":
        interview_round=interview_round+" Cleared"
        if interview_round not in status_options:
            add_status_option_to_job_applicant(interview_round)
        update_applicant_status_interview(applicant_id, interview_round)
    elif result == "Rejected":
        update_applicant_status_interview(applicant_id, "Rejected")
    elif result == "Under Review":
        interview_round=interview_round+" Scheduled"
        if interview_round not in status_options:
            add_status_option_to_job_applicant(interview_round)
        update_applicant_status_interview(applicant_id, interview_round)

    interview_doc.status = result
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
        fields=['name', 'job_title', 'status',
                'applicant_name', 'applicant_rating']
    )
    for application in job_applications:
        application['interview_summary'] = get_interview_details(
            application['name'])
    return job_applications


def get_applicant_data(applicant_name):
    applicant_data = frappe.get_value("Job Applicant", filters={"name": applicant_name}, fieldname=[
                                      "email_id", "job_title", "applicant_name"], as_dict=True)
    return (applicant_data.get("email_id"), applicant_data.get("applicant_name"), applicant_data.get("job_title"))


@frappe.whitelist()
def send_appointment_email(doc, method):
    applicant_email, applicant_name, position = get_applicant_data(
        doc.job_applicant)
   # Send email to the candidate
    frappe.sendmail(
        recipients=applicant_email,
        cc=frappe.get_doc('HR Manager Settings').hr_email_id,
        subject='Job Offer Notification',
        message=email_content_candidate(applicant_name, position),
        attachments=[{"file_url": doc.custom_appointment_letter}],
        now=True
    )
   # Send email to the interviewer
    frappe.sendmail(
        recipients=[doc.custom_interviewer_email],
        subject='Candidate Status Update',
        message=email_content_interviewer(
            applicant_name, applicant_email, position),
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
    if doc.status == 'Cleared':
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
            interview_record = frappe.db.sql(
                sql_query, (doc.job_applicant, i.interview_rounds), as_dict=True)
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
                message=content_for_hr_all_rounds_cleared(feedback, doc),
                now=True,
            )
    if (
        doc.status == "Rejected"
        and not doc.custom_rejection_email_sent
    ):
        applicant_email, applicant_name, position = get_applicant_data(
            doc.job_applicant)
        subject = "Your Application Status with KoreCent Solutions Pvt Ltd."

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
            message=email_content__compensatory_leave_request(
                employee_name, work_from_date, work_end_date),
            header="Compensatory Leave Request Notification"
        )


@frappe.whitelist()
def get_job_opening_rounds(job_title):
    return frappe.get_doc("Job Opening", job_title)


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
    contact = frappe.db.exists({"doctype": "Contact", "email_id": email})
    if contact:
        return 'exists'
    else:
        new_contact = frappe.get_doc({
            "doctype": "Contact",
            "first_name": name,
            "email_ids": [{"email_id": email, "is_primary": 1}],
            "phone_nos": [{"phone": mobile, "is_primary": 1}],
        })
        new_contact.insert()
        frappe.db.commit()
        return 'created'


@frappe.whitelist()
def send_job_applicant_creation_email(doc, method):
    frappe.sendmail(
        recipients=frappe.get_doc('HR Manager Settings').hr_email_id,
        subject='New job Applicant created notification',
        message=job_applicant_creation_hr(doc.job_title, doc.applicant_name),
        attachments=[{"file_url": doc.resume_attachment}],
        now=True
    )
    subject = f"Job application received for {doc.job_title} with KoreCent Solutions Pvt Ltd."
    frappe.sendmail(
        recipients=doc.email_id,
        subject=subject,
        message=email_content_for_successful_application(
            doc.applicant_name, doc.job_title),
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
def send_email_on_interview_scheduled(doc, method):
    current_date = getdate()
    schedule_date = getdate(doc.scheduled_on)
    try:
        # getting attachments from job applocant--------------------
        if (schedule_date >= current_date):
            attachments, applicant_name = frappe.db.get_value(
                'Job Applicant', {'name': doc.job_applicant}, ['resume_attachment', 'applicant_name'])
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
                message=prepare_email_content_on_interview_scheduled_to_applicat(
                    applicant_name, doc),
                now=True
            )
    except:
        pass


@frappe.whitelist(allow_guest=True)
def execute_job_offer_workflow():
    send_probation_completion_email()
    get_rejected_job_offers_created(2)
    get_rejected_job_offers_created(5)
    get_rejected_job_offers_created(7, closing=True)
    


@frappe.whitelist(allow_guest=True)
def restrict_to_create_job_offer(job_applicant_email, job_applicant_id):
    job_applicant_details = frappe.get_list(
        "Job Applicant",
        fields=["job_title"],
        filters={
            "email_id": job_applicant_email,
        }
    )
    job_interview_details = frappe.get_list(
        "Interview",
        fields=["interview_round", "status"],
        filters={
            "job_applicant": job_applicant_id
        }
    )

    candidate_interview_rounds = [entry['interview_round']
                                  for entry in job_interview_details]
    unique_candidate_interview_rounds = set(candidate_interview_rounds)
    unique_candidate_interview_rounds = sorted(
        unique_candidate_interview_rounds)
    job_title = job_applicant_details[0].job_title

    values = {'name': job_title}
    source_data = frappe.db.sql(
        """SELECT  ir.interview_rounds FROM `tabJob Opening` jo JOIN `tabInterview Rounds` ir ON jo.name = ir.parent WHERE     jo.name = %(name)s ORDER BY ir.idx""", values=values, as_dict=True)

    job_interview_rounds = [entry['interview_rounds'] for entry in source_data]
    unique_job_interview_rounds = set(job_interview_rounds)
    unique_job_interview_rounds = sorted(unique_job_interview_rounds)

    rounds_check = len(unique_candidate_interview_rounds) == len(
        unique_job_interview_rounds)

    return 1 if rounds_check else 0, job_interview_details


@frappe.whitelist()
def get_interview_feedback(interview_name):
    # Fetch records for the specific interview with child table data
    interview_feedback_records = frappe.get_list("Interview Feedback", filters={
                                                 "interview": interview_name}, fields=["name"],)
    # Fetch each record separately using get_doc
    feedback_docs = []
    for record in interview_feedback_records:
        feedback_doc = frappe.get_doc("Interview Feedback", record.name)
        feedback_docs.append(feedback_doc)

    return feedback_docs

# =========================  code for sending mail from job offer to its accept or reject state ======================== >>

@frappe.whitelist(allow_guest=True)
def send_Job_offer_email(doc, method):
    applicant_email, applicant_name, position = get_applicant_data(
        doc.job_applicant)
    # Send job offer notification to applicant and HR in CC
    frappe.sendmail(recipients=applicant_email,
                    subject='Job Offer Notification',
                    message=prepare_email_content_job_offer(
                        applicant_name, position, doc.custom_ctc, doc.name),
                    attachments=[{"file_url": doc.custom_offer_letter}],
                    cc=frappe.get_doc('HR Manager Settings').hr_email_id,
                    now=True)

    # email for HR notification about the job offer release
    frappe.sendmail(recipients=frappe.get_doc('HR Manager Settings').hr_email_id,
                    subject='Job Offer Released to Applicant - Action Update',
                    message=prepare_email_content_job_offer_hr(
                        position, applicant_name),
                    now=True)

# triggered when a candidate accepts a job offer & sends an acceptance email to the candidate, and generates a response page.


@frappe.whitelist(allow_guest=True)
def accept_offer(name):
    job_offer = frappe.get_doc("Job Offer", name)
    applicant_id = job_offer.job_applicant
    if job_offer.status in ("Accepted", "Rejected"):
        return handle_already_accepted_or_rejected(job_offer.status)

    job_offer.status = "Accepted"
    job_offer.save(ignore_permissions=True)
    job_offer.reload()
    frappe.db.commit()

    update_applicant_status_interview(applicant_id, "Job Offer Accepted")

    applicant_email, applicant_name, position = get_applicant_data(
        job_offer.job_applicant)
    # Send acceptance email to the candidate and HR in CC
    frappe.sendmail(recipients=applicant_email,
                    subject='Job Offer Accepted',
                    message=prepare_acceptance_email(position, job_offer),
                    cc=frappe.get_doc('HR Manager Settings').hr_email_id,
                    now=True)
    return frappe.respond_as_web_page("Offer Accepted", "<h1>Thanks for accepting the offer!</h1><p>You will receive the Appointment letter soon.</p>")

# Triggred when a candidate rejects a job offer ,sends a rejection email to the candidate and HR, and generates a response page.


@frappe.whitelist(allow_guest=True)
def reject_offer(name):
    job_offer = frappe.get_doc("Job Offer", name)
    applicant_id = job_offer.job_applicant
    if job_offer.status in ("Accepted", "Rejected"):
        return handle_already_accepted_or_rejected(job_offer.status)

    job_offer.status = "Rejected"
    job_offer.save(ignore_permissions=True)
    job_offer.reload()
    frappe.db.commit()

    update_applicant_status_interview(applicant_id, "Job Offer Rejected")

    applicant_email, applicant_name, position = get_applicant_data(
        job_offer.job_applicant)
    # Send rejection email to the candidate and HR
    frappe.sendmail(
        recipients=applicant_email,
        cc=frappe.get_doc('HR Manager Settings').hr_email_id,
        subject='Job Offer Rejected',
        message=prepare_rejection_email(job_offer.applicant_name),
        now=True
    )
    frappe.sendmail(
        recipients=applicant_email,
        cc=frappe.get_doc('HR Manager Settings').hr_email_id,
        subject='Job Offer Rejected',
        message=prepare_rejection_email_hr(
            job_offer.applicant_name, job_offer.job_applicant, position),
        now=True
    )
    return frappe.respond_as_web_page("Offer Rejected", "<h1>Offer Rejected</h1> <p>Thank you for considering our offer. If you change your mind, please feel free to contact us.</p>")

# ========================= End code for sending mail from job offer to its accept or reject state ======================== >>


# overriding for leave application calender view not to get rejected leaves data

@frappe.whitelist()
def get_events(doctype, start, end, field_map, filters=None, fields=None):
    field_map = frappe._dict(json.loads(field_map))
    fields = frappe.parse_json(fields)
    doc_meta = frappe.get_meta(doctype)

    for d in doc_meta.fields:
        if d.fieldtype == "Color":
            field_map.update({"color": d.fieldname})

    filters = json.loads(filters) if filters else []

    if not fields:
        fields = [field_map.start, field_map.end, field_map.title, "name"]

    if field_map.color:
        fields.append(field_map.color)

    start_date = "ifnull(%s, '0001-01-01 00:00:00')" % field_map.start
    end_date = "ifnull(%s, '2199-12-31 00:00:00')" % field_map.end

    if doctype == "Leave Application":
        filters += [
            [doctype, start_date, "<=", end],
            [doctype, end_date, ">=", start],
            [doctype, 'status', "not in", "Rejected"],
        ]
    else:
        filters += [
            [doctype, start_date, "<=", end],
            [doctype, end_date, ">=", start],
        ]

    fields = list({field for field in fields if field})
    return frappe.get_list(doctype, fields=fields, filters=filters)


# overriding standard function in __init__.py allowing attendance to mark if attendance_date is greater also
def mark_attendance_for_leave(self):
    pass


def mark_attendance_for_applied_leave(doc, method):
    from_date = getdate(doc.from_date)
    while from_date <= getdate(doc.to_date):
        if from_date.weekday() < 5:
            create_attendance_record(
                doc.employee, from_date, doc.leave_type, doc.half_day)
        from_date = add_days(from_date, 1)
    frappe.msgprint(
        (f"Attendance has been marked from {formatdate(getdate(doc.from_date), 'dd MMMM yyyy')} to {formatdate(doc.to_date,'dd MMMM yyyy')}"))


def create_attendance_record(employee, attendance_date, leave_type, half_day):
    attendance_doc = frappe.new_doc("Attendance")
    attendance_doc.employee = employee
    attendance_doc.attendance_date = attendance_date
    if (half_day == 1):
        attendance_doc.status = "Half Day"
    else:
        attendance_doc.status = "Work From Home" if leave_type == "Work from Home" else "On Leave"
    attendance_doc.leave_type = leave_type
    attendance_doc.save(ignore_permissions=True)
    attendance_doc.submit()


@frappe.whitelist(allow_guest=True)
def send_probation_completion_email():
    try:
        employees_data = []
        employees = frappe.get_all("Employee", filters={"employment_type": ["in", ["Intern", "Probation"]], "date_of_joining": (
            "<=", frappe.utils.add_months(frappe.utils.nowdate(), -6)), 'status': "Active"}, fields=['employee_name', "employment_type","name"])

        for employee in employees:
            employees_data.append({
                'employee_name': employee.get('employee_name'),
                'employment_type': employee.get('employment_type'),
                'name': employee.get('name')
            })
        frappe.log_error('employees_data', employees_data)

        if employees_data:
            frappe.log_error(' if employees_data', employees_data)
            hr_email = frappe.db.get_single_value('HR Manager Settings', 'hr_email_id')
            subject = "Employee type updation"
            message = f'''
                        Dear HR,<br>
                        Greetings of the day!<br>
                        Below enclosed are the employees completing their current employment type. Kindly take necessary action for their employment type.
                        <table cellspacing="0" border="1">
                            <tr>
                                <th>Employee Name</th>
                                <th>Employment Type</th>
                            </tr>
                        '''
            for emp_data in employees_data:
                message += f'''  
                <tr>
                    <td><a href="https://kcs-ess.frappe.cloud/app/employee/{emp_data['name']}">{emp_data['employee_name']}</td>
                    <td>{emp_data['employment_type']}</td>
                </tr>
                            '''

            message += """</table><br>
            Thanks and regards,<br>
            Team Korecent"""

            frappe.sendmail(recipients=[hr_email],
                            subject=subject, message=message)
    except Exception as e:
        frappe.log_error(f"Error: {str(e)}")

@frappe.whitelist()
def sendEmailDuringChangeInterviewMode(previous_mode, present_mode, interview_link, interview_address, applicant_email, interviewers):
    
    applicant_data = frappe.get_value("Job Applicant", filters={"name": applicant_email}, fieldname=[
                                      "email_id", "job_title", "applicant_name"], as_dict=True)
   # Send email to the candidate
    frappe.sendmail(
        recipients=applicant_email,
        cc=frappe.get_doc('HR Manager Settings').hr_email_id,
        subject='Interview mode is changed',
        message=email_content_candidate_for_changing_interview_mode(previous_mode, present_mode, interview_address, interview_link, applicant_data),
        
        now=True
    )

    interviewersArr = json.loads(interviewers)

    for each_interviewer in interviewersArr :
        print(each_interviewer)
        frappe.sendmail(
            recipients=each_interviewer['interviewer'],
            subject='Interview mode is changed',
            message=email_content_interviewer_for_changing_interview_mode(previous_mode, present_mode, interview_address, interview_link, applicant_data),
            now=True
        )
    
