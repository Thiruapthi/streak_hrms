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
                'applicant_name': applicantName,
                'status': newStatus
            },callback: function (r) {
                location.reload();
            }
        })
    },
    validate: function(frm) {
        frappe.call({
            method: "frappe.client.get_value",
            args: {
                doctype: "Appointment Letter",
                filters: {
                    job_applicant: frm.doc.job_applicant,
                },
                fieldname: 'appointment_date'
            },
            callback: function (response) {
                if (!response.exc) {
                    var appointmentdate = response.message.appointment_date;
                    if (frm.doc.date_of_joining != appointmentdate) {
                        frappe.msgprint(__("Date of joining mismatch with the date in the appointment letter"));
                        frappe.validated = false;
                    }
                } else {
                    console.error('Error fetching applicant status: ' + response.exc);
                }
            }
        });

        if (frm.doc.date_of_joining > frm.doc.boarding_begins_on) {
            frappe.msgprint(__("Boarding date can't be before joining date"));
            frappe.validated = false;
        }
        
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
                        frappe.msgprint('Cannot save the Employee Onboarding for a rejected applicant.');
                        frappe.validated = false;
                    }
                } else {
                    console.error('Error fetching applicant status: ' + response.exc);
                }
            }
        });
    }
})