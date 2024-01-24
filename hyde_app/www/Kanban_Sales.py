import frappe

@frappe.whitelist(allow_guest=True)
def update_custom_select_field(a=None,b=None):
    sales_stages = frappe.get_all("Sales Stage", filters={}, fields=["stage_name"])
    stage_names = [stage.get("stage_name") for stage in sales_stages]
    custom_field = frappe.db.exists("Custom Field", {"name": "Opportunity-custom_test"})
    if (custom_field):
        frappe.db.set_value("Custom Field", custom_field, "options", "\n".join(stage_names))