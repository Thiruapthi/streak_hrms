frappe.ui.form.on('Appointment Letter',{
    after_save(frm){
        let applicantName = frm.doc.job_applicant
        let newStatus  = "Appointment Letter Released"
        frappe.call({
            method: 'hyde_app.api.update_applicant_status_interview',
            args: {
                'applicant_name': applicantName,
                'status': newStatus
            }
    })
}
})