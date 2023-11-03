import frappe

@frappe.whitelist()
def update_applicant_status_interview(applicant_name, status):
    try:
        applicant = frappe.get_doc("Job Applicant", applicant_name)
        applicant.status = status
        applicant.save()
        applicant.reload()
        frappe.db.commit()
        frappe.publish_realtime('applicant_status_update', {
            'doc': applicant,
            'applicant_name': applicant_name,
            'status': status
        })
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
    # doc = []
    # print(source_data,'source_data\n\n\n\n\n\n\n\n\n\n\n')
    # # Get the source document based on the job title
    return source_data
    # # Iterate through the source child table and extract data
    # for source_row in source_doc.custom_round:
    #     doc.append({
    #         "interview_rounds": source_row.interview_rounds
    #     })
    # print(doc,"doc\n\n\n\n\n\n\n\n\n")
    # return doc
    # source_doctype = "Job Opening"
    # doc = []
    # # target_doctype = "Job Applicant"
    # print("\n\n\n\n\n\n",'interview round',"\n\n\n\n\n\n\n\n")
    # # Get a list of source documents
    # # source_documents = frappe.get_doc(source_doctype, filters={"job_title": job_title})

    # # for source_doc in source_documents:
    #     # Load the source document
    # source_doc = frappe.get_doc(doctype=source_doctype, job_title= job_titles)
    # print(source_doc,"\n\n\n\n\n\n\n\n")   
    #     # Add the source child table data to the target child table
    # for source_row in source_doc.custom_round:
    #         print(source_row)
    #         doc.append{
    #             "interview_rounds": source_row.interview_rounds
    #         }
    # return doc



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