frappe.ui.form.on('Employee',{
    after_save : function(frm){
        let applicantName = frm.doc.employee_name
        let newStatus = 'Applicant Onboarded'
        frappe.call({
            method: 'hyde_app.api.update_applicant_status_interview',
            args: {
                'applicant_name': applicantName,
                'status': newStatus
            }
    })
    }
})