import frappe
from datetime import datetime, timedelta

# Email content for the applicent when appointment letter created


def email_content_candidate(applicant_name, position):
    return f"""\
        <p>Dear {applicant_name},</p>
        <p>Greetings of the day!</p>
        <p>Heartiest congratulations! We are pleased to offer you the position of {position} with Korecent Solutions Pvt. Ltd.</p>
        <p>Below enclosed is your appointment letter. Please let us know incase of any assistance.</p>
        <p>Welcome aboard !</p>
        <p>Thanks and regards,</p>
        <p>HR- Team KoreCent</p>
    """


def email_content_candidate_for_changing_interview_mode(previous_mode, present_mode, interview_address, interview_link, applicant_data, job_title):
    if present_mode == 'Online':
        return f"""\
            <p>Dear {applicant_data['applicant_name']},</p>
            <p>Greetings of the day.</p>
            <p>We want to inform you that your interview mode for the position of {job_title} has been updated to online mode now. The interview link has been enclosed below: </p>
            <p>Link: <a href='{interview_link}' >Interview Link</a></p>
            <p>Please confirm your availability within one day of receiving in this trail email.</p>
            <p>Wishing you all the best.</p>
            <p>Thanks and regards</p>
            <p>HR Team</p>
            <p>Contact us:</p>
            <p>Email: hr@korecent.com</p>
            <p>Mobile no: + 91 9041025546</p>
        """
    else:
        return f"""\
            <p>Dear {applicant_data['applicant_name']},</p>
            <p>Greetings of the day.</p>
            <p>We want to inform you that your interview mode for the position of {job_title} has been updated to to offline mode now. The venue of the interview has as been enclosed below:</p>
            <p>Office address:{interview_address}</p>
            <p>Please confirm your availability within one day of receiving in this trail email.</p>
            <p>Wishing you all the best.</p>
            <p>Thanks and regards</p>
            <p>HR Team</p>
            <p>Contact us:</p>
            <p>Email: hr@korecent.com</p>
            <p>Mobile no: + 91 9041025546</p>
        """


def email_content_interviewer_for_changing_interview_mode(previous_mode, present_mode, interview_address, interview_link, applicant_data, job_title,interviewer_name):
    if present_mode == 'Online':
        return f"""\
            <p>Dear {interviewer_name},</p>
            <p>Greetings of the day.</p>
            <p>We want to inform you that the interview of {applicant_data['applicant_name']} for the position of {job_title} has been updated to online mode now. The interview link has been enclosed below:</p>
            <p>Link: <a href='{interview_link}' >Interview Link</a></p>
            <p>Please ensure your availability for the interview and incase of any rescheduling let us know 1 day in advance.</p>
            <p>Thanks and regards</p>
            <p>HR Team</p>
            <p>Contact us:</p>
            <p>Email: hr@korecent.com</p>
            <p>Mobile no: + 91 9041025546</p>
        """
    else:
        return f"""\
            <p>Dear {interviewer_name},</p>
            <p>Greetings of the day.</p>
            <p>We want to inform you that the interview of {applicant_data['applicant_name']} for the position of {job_title}  has been updated to offline mode now.</p>
            <p>The venue of the interview has as been enclosed below:</p>
            <p>Office address:{interview_address}</p>
            <p>Thanks and regards</p>
            <p>HR Team</p>
            <p>Contact us:</p>
            <p>Email: hr@korecent.com</p>
            <p>Mobile no: + 91 9041025546</p>
        """

# Email content for the interviewer when appointment letter created


def email_content_interviewer(applicant_name, applicant_email, position):
    return f"""\
        <p>Dear Interviewer,</p>
        <p>Greetings! We have sent the appointment letter to the candidate, {applicant_name} ({applicant_email}), for the position of {position} with Korecent Solutions Pvt. Ltd.</p>
        <p>If you have any additional feedback or instructions, please feel free to share.</p>
        <p>Thanks and regards,</p>
        <p>HR- Team KoreCent</p>
    """

# email template for the applicant when rejected in interview


def email_content_after_interview_rejection(applicant_name):
    return f"""\
        <p>Dear {applicant_name},</p>
        <p>Greetings of the day!</p>
        <p>Thank you for completing the interview process with KoreCent Solutions Pvt Ltd. We acknowledge your commendable background and appreciate the opportunity to learn more about you.</p>
        <p>Unfortunately, we will not be moving forward with your application at this time as our current requirements do not align with your skills.</p>
        <p>We have your details in our database and will reach out to you in case a suitable opening arises in our organization.</p>
        <p>Wishing you all the very best.</p>
        <p>Thanks and regards,<br>HR - Team KoreCent</p>
    """


def email_content__compensatory_leave_request(employee_name, work_from_date, work_end_date):
    return f"""
        <br>Dear {employee_name},<br><br>
        Greetings of the day!<br><br>
        Your compensatory leave request has been approved for the From Date: {work_from_date} To End Date: {work_end_date}. Balance of the same has been added to your leaves.<br><br><br>
        Thanks and regards,<br>
        HR-Team KoreCent
    """

# template for applicent when job application is created


def email_content_for_successful_application(applicant_name, job_title):
    return (
        f"<p>Dear {applicant_name},</p>"
        "<p>Greetings of the day!</p>"
        "<p>Thank you for your interest in KoreCent Solutions Pvt Ltd. We have received your application "
        f"for {job_title}. Currently, we are reviewing your application and will get back to you "
        "in case you are selected for further hiring processes.</p>"
        "<p>Wishing you all the very best.</p>"
        "<p>Thanks and regards,<br></p>"
        "<p>HR - Team KoreCent</p>"
    )

# template for HR when job application is created


def job_applicant_creation_hr(job_title, applicant_name):
    return f"""\
        Dear HR,<br><br>
        Greetings of the day!<br><br>
        We want to inform you that a new job application has been submitted for the { job_title } .<br>
        The name of the candidate is { applicant_name } and his resume has been attached for your reference along with the website link : {"https://kcs-ess.frappe.cloud/" }<br><br>
        Kindly do the needful.<br>
        Thanks and regards <br>
        HR- Team KoreCent
    """


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


def content_for_hr_all_rounds_cleared(feedback, doc):
    table_rows = ""
    for name, interview_data in feedback['interviews'].items():
        interviewers_list = frappe.get_list("Interview Detail", filters={
                                            "parent": name, "parenttype": "Interview"}, pluck="custom_interviewer_name")
        table_rows += f"""
        <tr>
            <td style="padding:5px;">{interview_data['interview_round']}</td>
            <td style="padding:5px;">{interview_data['status']}</td>
            <td style="padding:5px;">{interview_data['average_rating']}</td>
            <td style="padding:5px;">{", ".join(interviewers_list)}</td>
        </tr>"""
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
    return message

#  Template for applicant when job offer is created


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

# sending email on creation of interview to interviewer-------------------


def prepare_email_content_on_interview_scheduled(doc):
    return f"""\
            <p>Dear {doc.interview_details[0].custom_interviewer_name}, </p>
            <p>Greetings of the day! </p>
            <p>An interview has been scheduled for {doc.designation} on {doc.scheduled_on} at {doc.from_time}. Candidate name is {doc.custom_job_applicant_name}.</p> <p>It will be a { doc.interview_round }.</p>            
            <p>Below enclosed is the resume for your reference </a>.</p>
            {f"<p>Interview Link: {doc.custom_interview_link}</p>" if doc.custom_interview_type == "Online" else f"<p>Address: {doc.custom_address}</p>"}
            {f"<p>Apptitude round test portal link please share this link with the applicant once they join the interview link:<a href={doc.custom_exam_portal_link}>Apptitude Test Link</a></p>"if doc.interview_round=="Aptitude test" else ""}
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


def prepare_email_content_on_interview_scheduled_to_applicat(applicant_name, doc):
    return f"""\
            <p>Dear { applicant_name },</p>
            <p>Greetings of the day!</p>
            <p>We are pleased to inform you that your interview has been scheduled for { doc.designation } on { doc.scheduled_on } at { doc.from_time }.</p><p>It will be a { doc.interview_round }.</p>
            {f"<p>Interview Link: {doc.custom_interview_link}</p>" if doc.custom_interview_type == "Online" else f"<p>Address: {doc.custom_address}</p>"}
            <p>Please confirm your availability for the interview within 1 day of receiving the email.</p>
            <p>Wishing you the best for your interview.</p>
            <p>Thanks and regards,</p>
            <p>HR-Team KoreCent</p>
            <h3>Contact us:</h3>
            <p>Email:{frappe.get_single("HR Manager Settings").hr_email_id}</p>
            <p>Mobile no: + 91 9041025546</p>
            """

#  Template to notify HR when job offer is created

def prepare_email_content_job_offer_hr(position, applicant_name):
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

# template for applicent when he accepts the offer


def prepare_acceptance_email(job_position, job_offer):
    return f"""
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

# template for applicent when he rejects the offer


def prepare_rejection_email(applicant_name):
    return f"""
        <p>Dear {applicant_name},</p>
        <p>Greetings of the day!</p>
        <p>We are sorry to know that you have decided to decline the job offer. We want to reach out in order to address your concerns and feedback. Kindly let us know your availability so that we can plan a call accordingly.</p>
        <p>Thanks and regards,</p>
        <p>HR- Team KoreCent</p>
        """

# template for HR when applicent rejeects the offer


def prepare_rejection_email_hr(applicant_name, job_applicant, job_position):
    return f"""
        <p>Dear {frappe.get_doc('HR Manager Settings').hr_manager_name},</p>
        <p>Greetings of the day!</p>
        <p>We want to inform you that the {applicant_name}({job_applicant}) who was offered the {job_position} position with Korecent Solutions Pvt. Ltd has rejected the job offer. An email has been sent to them seeking their availability to address their concerns.</p>
        <p>Kindly plan to connect with them accordingly.</p>
        <p>Thanks and regards,</p>
        <p>HR- Team KoreCent</p>
        """


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
            ["job_title"],
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
                "<p>Thank you for your completing the interview process KoreCent Solutions Pvt ltd. You have a commendable background and we appreciate you giving us the opportunity to learn more about you. Unfortunately since you have not taken any necessary action after releasing your  job offer, we will not be moving forward with your application.</p>"
                "<p>We encourage you to continue to review our careers site and apply for the positions that interests you.</p>"
                "<p>Wishing you all the very best.<br>Thanks and regards,<br>HR- Team KoreCent</p>"
            )
        send_reminder_email(doc.applicant_email, subject, message)


def send_hr_leave_notification(doc, method):
    hr_email = frappe.db.get_single_value('HR Manager Settings', 'hr_email_id')
    if doc.workflow_state == "HR Approval Pending" and hr_email:
        subject = "Leave Application Notification"
        message = (
            f"<h1>Leave Application Notification</h1>"
            "<p>Dear Concerned,</p>"
            f"<p>{doc.employee_name} has applied for {doc.custom_leave_segment_choice if doc.half_day else 'full day'} {doc.leave_type} From {doc.from_date} To {doc.to_date}.</p>"
            f"<p>Respective leave approver : {doc.leave_approver_name}.</p>"
            f"<p>Reason: {doc.description}.</p>"
            f"<p> Leave Balance Before Application {doc.leave_balance}.</p>"
            "<p>Thanks and regards,</p>"
            "<p>HR- Team KoreCent.</p>"
        )
        frappe.sendmail(
            recipients=hr_email,
            subject=subject,
            message=message,
            now=True
        )


def notify_interview_rescheduling(self):
    message = (f"""
    <p>Dear {self.custom_job_applicant_name}</p>
    <p>Greetings of the day!</p>
    <p>We are pleased to inform you that your interview has been rescheduled for {self.designation} to {self.scheduled_on} at {self.from_time}-{self.to_time}.</p>
    <p>It will be a {self.interview_round}.</p>
    {f"<p>Interview Link: {self.custom_interview_link}</p>" if self.custom_interview_type == "Online" else f"<p>Address: {self.custom_address}</p>"}
    <p>Please confirm your availability for the interview within 1 day of receiving the email.</p>
    <p>Wishing you the best for your interview.</p>
    <p>Thanks and regards,</p>
    <p>HR- Team KoreCent.</p>
    <h3>Contact us:</h3>
    <p>Email:{frappe.get_single("HR Manager Settings").hr_email_id}</p>
    <p>Mobile no: + 91 9041025546</p>
    """)
    return message



@frappe.whitelist(allow_guest=True)
def get_open_jobs():
    docs = frappe.get_list("Job Opening", order_by="creation desc")
    li=[]
    for i in docs:
        if i.status!="Closed":
            li.append(frappe.get_doc("Job Opening",i.name).as_dict())
    return li
    