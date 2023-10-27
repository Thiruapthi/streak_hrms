frappe.ui.form.on("Sales Stage", {
    after_save: function (frm) {
        frappe.call({
            method: 'hyde_app.www.test.update_custom_select_field',
            args: {},
            callback: function(r) {
                if (!r.exc) {
                    let d=frm
                }
            }
        });
        }
    
})