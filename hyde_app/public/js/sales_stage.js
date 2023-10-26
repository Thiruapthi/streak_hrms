frappe.ui.form.on("Sales Stage", {
    after_save: function(frm){
        frappe.call({
            method: "hyde_app.www.test.write_options",
            args:{}
        }).done((r)=>{
            console.log(r)
        })
    }
});
