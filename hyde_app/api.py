import frappe

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
    values = {'job_title':job_titles}
    source_data = frappe.db.sql("""SELECT  ir.interview_rounds FROM `tabJob Opening` jo JOIN `tabInterview Rounds` ir ON jo.name = ir.parent WHERE     jo.job_title = %(job_title)s""",values = values,as_dict=True   )
    
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
       application['interviews'] = get_interviews(application['name'])
   return job_applications


def get_interviews(applicant_name):
   interviews = frappe.get_all(
       'Interview Feedback',
       filters={
           'job_applicant': applicant_name
       },
       fields=['interview_round', "interviewer",'result','feedback']
   )
   return interviews

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
          subject = 'Job Offer Approval'
          message =    message = f'''\
                <p>Dear HR Team,</p>
                <p>Greetings! We would like to inform you that the job applicant, {doc.job_applicant}, has successfully cleared all interview rounds for the position of {doc.job_opening} with Korecent Solutions Pvt. Ltd.</p>
                <p>The applicant is now ready for the job offer release. Please proceed with the necessary steps to prepare and send the job offer.</p>
                <p>Thanks and regards,</p>
                <p>Automated Notification System</p>
            '''
          frappe.sendmail(
          recipients=[recipient_email],
          subject=subject,
          message=message,
          now=True,
          )

def send_custom_email(recipients, subject, message, attachments=None, cc_recipients=None):
    email_args = {
        "recipients": recipients,
        "subject": subject,
        "message": message,
        "attachments": attachments,
        "now": True
    }

    if cc_recipients:
        email_args["cc"] = cc_recipients
    if attachments:
        email_args["attachments"] = attachments

    frappe.sendmail(**email_args)

@frappe.whitelist()
def send_Job_offer_email(doc,method):
    applicant_data = frappe.get_value(
        "Job Applicant",
        {"name": doc.job_applicant},
        ["email_id", "job_title", "applicant_name"],
        as_dict=True
    )
    applicant_email = applicant_data.get("email_id")
    applicant_name = applicant_data.get("applicant_name")
    position = applicant_data.get("job_title")
    ctc = doc.custom_ctc
    # Email content for the candidate
    email_content_candidate = f"""\
        <p>Dear {applicant_name},</p>
        <p>Greetings of the day!</p>
        <p>Heartiest congratulations! We are pleased to offer you the position of {position} with Korecent Solutions Pvt. Ltd. at {ctc} CTC.</p>
        <p>Please take the necessary action on the below enclosed link within the next 7 days:</p>
        <p>Below enclosed is your detailed job offer pdf.</p>
        <a href="{frappe.utils.get_url()}/api/method/hyde_app.api.accept_offer?name={doc.name}" onclick="this.style.pointerEvents = 'none'; this.style.background = '#ccc';" style="background-color: #4CAF50; color: #fff; padding: 10px 20px; text-decoration: none; display: inline-block; border-radius: 5px; margin-right: 10px;">Accept</a>
        <a href="{frappe.utils.get_url()}/api/method/hyde_app.api.reject_offer?name={doc.name}" onclick="this.style.pointerEvents = 'none'; this.style.background = '#ccc';" style="background-color: #FF5733; color: #fff; padding: 10px 20px; text-decoration: none; display: inline-block; border-radius: 5px;">Reject</a>
        <p>Thanks and regards,</p>
        <p>HR- Team KoreCent</p>
    """
    send_custom_email(recipients=applicant_email,
                       subject='Job Offer Notification', 
                       message=email_content_candidate,
                       attachments=[{"file_url": doc.custom_offer_letter}],
                       cc_recipients=frappe.get_doc('HR Manager Settings').hr_email_id)

    # Email content for notifying HR about the person who released the job offer
    released_by = frappe.session.user  
    user_fullname = frappe.get_value("User", released_by, "username")
    email_content_hr_released_by = f"""\
    <p>Dear {frappe.get_doc('HR Manager Settings').hr_manager_name}</p>
    <p>This is to inform you that the job offer for the position of {position} to {applicant_name} has been released.</p>
    <p>The offer was extended by: {user_fullname} ({released_by})</p>
    <p>Kindly take note of this action in your records.</p>
    <br>
    <br>
    <p>Auto-generated mail.</p>
    <p>Thank you.</p>
    """
    send_custom_email(recipients=frappe.get_doc('HR Manager Settings').hr_email_id,
                      subject='Job Offer Released to Applicant - Action Update', message=email_content_hr_released_by,
                      attachments=None,
                      cc_recipients=None)


@frappe.whitelist(allow_guest=True)
def accept_offer(name):
    job_offer = frappe.get_doc("Job Offer", name)
    job_offer.status = "Accepted"
    job_offer.save()
    frappe.db.commit()
    attachments = frappe.get_all("File", filters={"attached_to_doctype": "Job Offer", "attached_to_name": name}, fields=["file_url"])
    applicant_data = frappe.get_value(
        "Job Applicant",
        {"name": job_offer.job_applicant},
        ["email_id",'job_title'],
        as_dict=True
    )
    applicant_email = applicant_data.get("email_id")
    job_position = applicant_data.get("job_title")

    subject = 'Job Offer Accepted'
    email_content = f"""
        <p>Dear {job_offer.applicant_name},</p>
        <p>Greetings of the day!</p>
        <p>Heartiest congratulations! We are pleased to have you with Korecent Solutions Pvt. Ltd. as a {job_position}. Below enclosed is your detailed job offer PDF.</p>
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
    frappe.sendmail(
            recipients = applicant_email,
            cc=frappe.get_doc('HR Manager Settings').hr_email_id,
            subject = subject,
            message=email_content,
            attachments=attachments,
            now = True
        )
    page_content = """
        <html>
        <head>
            <title>Offer Accepted</title>
        </head>
        <body>
            <h1>Thanks for accepting the offer!</h1>
            <p>You will receive the offer letter soon.</p>
        </body>
        </html>
        """
    return frappe.respond_as_web_page("Offer Accepted", page_content)


@frappe.whitelist(allow_guest=True)
def reject_offer(name):
    job_offer = frappe.get_doc("Job Offer", name)
    job_offer.status = "Rejected"
    job_offer.save()
    frappe.db.commit()
    applicant_data = frappe.get_value(
        "Job Applicant",
        {"name": job_offer.job_applicant},
        ["email_id","job_title"],
        as_dict=True
    )
    applicant_email = applicant_data.get("email_id")
    job_position = applicant_data.get("job_title")


    email_content = f"""
        <p>Dear {job_offer.applicant_name},</p>
        <p>Greetings of the day!</p>
        <p>We are sorry to know that you have decided to decline the job offer. We want to reach out in order to address your concerns and feedback. Kindly let us know your availability so that we can plan a call accordingly.</p>
        <p>Thanks and regards,</p>
        <p>HR- Team KoreCent</p>
            """
    frappe.sendmail(
      recipients=applicant_email,
      cc=frappe.get_doc('HR Manager Settings').hr_email_id,
      subject='Job Offer Rejected',
      message=email_content,
      now = True
    )

    email_content = f"""
        <p>Dear {frappe.get_doc('HR Manager Settings').hr_manager_name},</p>
        <p>Greetings of the day!</p>
        <p>We want to inform you that the {job_offer.job_applicant} who was offered the {job_position} position with Korecent Solutions Pvt. Ltd has rejected the job offer. An email has been sent to them seeking their availability to address their concerns.</p>
        <p>Kindly plan to connect with them accordingly.</p>
        <p>Thanks and regards,</p>
        <p>HR- Team KoreCent</p>
            """
    frappe.sendmail(
      recipients=applicant_email,
      cc=frappe.get_doc('HR Manager Settings').hr_email_id,
      subject='Job Offer Rejected',
      message=email_content,
      now = True
    )
    page_content = """
    <html>
    <head>
        <title>Offer Rejected</title>
    </head>
    <body>
        <h1>Offer Rejected</h1>
        <p>Thank you for considering our offer. If you change your mind, please feel free to contact us.</p>
    </body>
    </html>
    """
    return frappe.respond_as_web_page("Offer Rejected", page_content)

 


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
def check_all_interviews_cleared(job_applicant):
    interviews = frappe.get_all("Interview", filters={"job_applicant": job_applicant}, fields=["status"])
    if not interviews:
        return "No interviews found"
    for interview in interviews:
        if interview.get("status") != "Cleared":
            return "Not all interviews are cleared"
    return "All interviews are cleared"


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
