import frappe

@frappe.whitelist()
def update_applicant_status_interview(applicant_name, status):
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


@frappe.whitelist(allow_guest=True)
def job_applicant_contact(email,mobile,name):
    contact = frappe.get_list("Contact", filters={"email_id": email})
    c= frappe.new_doc("Contact")
    # print(c,"c\n\n\n\n\n\n\n\n")
    # Update or create the `Csontact` document
    if not contact:
        # print(contact,"\n\n\n\n\n\n\n\n")
        # print(c,"c\n\n\n\n\n\n\n\n")
        c.first_name = name
        c.email_id=email

    if mobile:
        # print(mobile,"wokring\n\n\n\n\n")
        c.first_name = name
        c.append("phone_nos", {
            "phone": mobile,
            "is_primary_mobile_no": 1
        })

    # # Add email_id to the email_ids child table
        c.append("email_ids", {
            "email_id": email,
            "is_primary": 1
        })

    # Save the `Contact` document
    c.save()
    frappe.db.commit()

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

import frappe
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
    print(frappe.utils.get_url())
    # Get multiple values from the document based on the job applicant's name
    applicant_data = frappe.get_value(
        "Job Applicant",
        {"name": doc.job_applicant},
        ["email_id", "job_title", "applicant_name"],
        as_dict=True
    )

    # Access individual values as needed
    applicant_email = applicant_data.get("email_id")
    applicant_name = applicant_data.get("applicant_name")
    position = applicant_data.get("job_title")
    # ctc = doc.ctc

    # Compose the HTML email content using the provided template and dynamic values
    email_content = f"""\
        <html>
        <head>
            <style>
                /* Add your styling here */
            </style>
        </head>
        <body>
            <p>Dear {applicant_name},</p>
            <p>Greetings of the day!</p>
            <p>Heartiest congratulations! We are pleased to offer you the position of {position} Business Analyst with Korecent Solutions Pvt. Ltd. at {1} CTC.</p>
            <p>Please take the necessary action on the below enclosed link within the next 7 days:</p>
               <a href="{ frappe.utils.get_url() }/api/method/hyde_app.api.accept_offer?name={applicant_email }" 
   onclick="this.style.pointerEvents = 'none'; this.style.background = '#ccc';" 
   style="background-color: #4CAF50; color: #fff; padding: 10px 20px; text-decoration: none; display: inline-block; border-radius: 5px; margin-right: 10px;">Accept</a>

<a href="{ frappe.utils.get_url() }/api/method/hyde_app.api.reject_offer?name={ applicant_email }" 
   onclick="this.style.pointerEvents = 'none'; this.style.background = '#ccc';" 
   style="background-color: #FF5733; color: #fff; padding: 10px 20px; text-decoration: none; display: inline-block; border-radius: 5px;">Reject</a>
    </div>
            <p>Thanks and regards,</p>
            <p>HR- Team KoreCent</p>
        </body>
        </html>
    """

    # Send HTML email
    frappe.sendmail(
        recipients=applicant_email,
        cc='oorjaa@korecent.com',
        subject='Job Offer Rejected',
        message=email_content,
        now=True
    )






#code with dummy data

@frappe.whitelist(allow_guest=True)
def accept_offer():
  subject = 'Job Offer Accepted'
   # Create the HTML content for the email
  email_content = """
  <html>
  <head>
      <title>Job Offer Accepted</title>
  </head>
  <body>
      <p>Dear Recipient,</p>
      <p>We are pleased to inform you that your acceptance of the job offer for the position of Frappe Developer at KCS has been received.</p>
      <p>Please find attached the formal offer letter. Kindly review it for further instructions.</p>
      <p>Thank you for choosing to join our team.</p>
      <p>Best regards,</p>
      <p>Your Name</p>
  </body>
  </html>
  """
  frappe.sendmail(
      recipients = 'umakanth@korecent.com',
      subject = subject,
      message=email_content,
      attachments=[{"file_url": "/files/artturi-jalli-g5_rxRjvKmg-unsplash.jpg"}],
      now = True
  )
  # Create an HTML page response
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
def reject_offer():
  frappe.sendmail(
      recipients='umakanth@korecent.com',
      subject='Job Offer Rejected',
      message='Your job offer has been rejected.',
      now = True
  )
  frappe.sendmail(
      recipients='oorjaa@korecent.com',
      subject='Job Offer Rejected',
      message='Your job offer has been rejected.',
      now = True
  )
  # Create an HTML page response
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
          recipient_email = 'umakanth@korecent.com'
          subject = 'Job Offer Approval'
          message = f'All interview rounds have been cleared for the candidate {doc.job_applicant}. Please proceed to release the job offer.'
          frappe.sendmail(
          recipients=[recipient_email],
          subject=subject,
          message=message,
          now=True,
          )

