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