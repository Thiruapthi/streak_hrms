frappe.ui.form.on('Employee',{
    after_save: function (frm) {
        let applicantName = frm.doc.employee_name
        let newStatus = 'Applicant Onboarded'
        let applicantId = '';
        frappe.call({
            method: 'hyde_app.api.get_job_applicant_id',
            args: {
                'applicant_name': applicantName,
            }, callback: function (r) {
                applicantId = r.message
            }
        })
        setTimeout(function() {
        if (applicantId!==undefined){
            frappe.call({
                method: 'hyde_app.api.update_applicant_status_interview',
                args: {
                    'applicant_name': applicantId,
                    'status': newStatus
                }, callback: function (r) {
                    location.reload();
                }
            })
        }
        }, 1000);
    },
    validate: function(frm) {
        if (frm.doc.job_applicant){
        frappe.call({
            method: "frappe.client.get_value",
            args: {
                doctype: "Job Applicant",
                filters: {
                    name: frm.doc.job_applicant,
                },
                fieldname: 'status'
            },
            callback: function (response) {
                if (!response.exc) {
                    var applicantStatus = response.message.status;
                    if (applicantStatus === 'Rejected') {
                        frappe.msgprint('Cannot save the Employee for a rejected applicant.');
                        frappe.validated = false;
                    }
                } else {
                    console.error('Error fetching applicant status: ' + response.exc);
                }
            }
        });
    }
    }
})