import frappe

@frappe.whitelist(allow_guest=True)
def get_all_roles():
	user_roles = frappe.get_roles(frappe.session.user)
	return user_roles

