frappe.ui.form.on('Job Offer', {
	after_save(frm) {
        let applicantName = frm.doc.job_applicant;  // Get the name of the saved applicant
        let   newStatus = ''// Specify the new status
        if (frm.doc.status === "Awaiting Response") {
            newStatus = "Job Offer Released";
        }else if(frm.doc.status ==="Accepted"){
            newStatus = "Job Offer Accepted";
        }
        else if(frm.doc.status === "Rejected"){
            newStatus = "Job Offer Rejected";
        }
        
        frappe.call({
            method: 'hyde_app.api.update_applicant_status_interview',    
            args: {
                applicant_name: applicantName,
                new_status: newStatus
            }
        });
    },
    validate: function(frm) {
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
                        frappe.msgprint('Cannot save the Job Offer for a rejected applicant.');
                        frappe.validated = false;
                    }
                } else {
                    console.error('Error fetching applicant status: ' + response.exc);
                }
            }
        });
    }
})