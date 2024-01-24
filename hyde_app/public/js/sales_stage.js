frappe.ui.form.on("Sales Stage", {
    after_save: function (frm) {
        frappe.call({
            method: 'hyde_app.www.Kanban_Sales.update_custom_select_field',
            args: {},
            callback: function(r) {
               let result=r.result;
            }
        });
        }
    
})