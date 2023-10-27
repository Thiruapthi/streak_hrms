frappe.ui.form.on('Employee Onboarding', {
    setup: function (frm) {
        frm.set_query("job_applicant", function () {
            return {
                filters: {
                    "status": "Appointment Letter Released",
                }
            };
        });
    },
    after_save(frm) {
        let applicantName = frm.doc.job_applicant
        let newStatus = 'Employee Onboarding In Progress'
        frappe.call({
            method: 'hyde_app.api.update_applicant_status_interview',
            args: {
                applicant_name: applicantName,
                new_status: newStatus
            }
        })
    }
})