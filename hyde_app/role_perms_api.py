import frappe
from frappe import _
from frappe.utils import  getdate

@frappe.whitelist()
def get_role_permissions(role):
    """Returns permissions with value 1 for a given role"""
    perms = frappe.get_all(
        "DocPerm",
        fields=["parent", "role", "read", "write", "create", "submit", "cancel", "delete", "amend", "report", "export", "import", "share", "print", "email", "select", "set_user_permissions"],
        filters={"role": role},
    )

    custom_perms = frappe.get_all(
        "Custom DocPerm",
        fields=["parent", "role", "read", "write", "create", "submit", "cancel", "delete", "amend", "report", "export", "import", "share", "print", "email", "select", "set_user_permissions"],
        filters={"role": role},
    )

    doctypes_with_custom_perms = frappe.get_all("Custom DocPerm", pluck="parent", distinct=True)

    for p in perms:
        if p.parent not in doctypes_with_custom_perms:
            custom_perms.append(p)
	
    permissions = []
   
    for perm in custom_perms:
        # Check if any permission field has a value of 1 (checked)
        if any(perm[field] == 1 for field in perm.keys() if field not in ["parent", "role"]):
           
            permission = {key: value for key, value in perm.items() if value == 1}
            permission["role"] = perm["role"]
            permission["parent"] = perm["parent"]
            permissions.append(permission)
    return permissions


@frappe.whitelist()
def hideing_leave_without_pay(doctype, txt, searchfield, start, page_len, filters):
   user = filters.get("employee_id")
   doc = frappe.get_doc('Employee', user)
   joining_date = doc.date_of_joining
   employment = doc.employment_type
   current_date = getdate()
   days_difference = (current_date - joining_date).days
   if employment == "Permanent" and days_difference > 365:
       return  frappe.db.sql(""" select name from `tabLeave Type`""")
   else:
       return frappe.db.sql(""" select name from `tabLeave Type` where name != "Leave Without Pay" """)
  
