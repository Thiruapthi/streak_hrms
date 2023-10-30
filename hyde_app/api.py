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

