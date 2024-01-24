frappe.ui.form.on('Appointment Letter',{
    job_applicant: function(frm){
        frappe.call({
            method: 'hyde_app.api.get_latest_interview',
            args: {
                job_applicant: frm.doc.job_applicant
            },
            callback: function(r) {
                if (r.message) {
                    frm.set_value('custom_interviewer_email', r.message)
                }else{
                    frm.set_value('custom_interviewer_email','')

                }
            }
        });
     },
    after_save(frm){
        let applicantName = frm.doc.job_applicant
        let newStatus  = "Appointment Letter Released"
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
                    frappe.msgprint('Cannot save the Appointment Letter for a rejected applicant.');
                    frappe.validated = false;
                }
            } else {
                console.error('Error fetching applicant status: ' + response.exc);
            }
        }
    });
    frappe.call({
        method: 'hyde_app.api.get_latest_job_offer_date',   
        args: {
            'job_applicant': frm.doc.job_applicant,
        },
        callback: function (r) {
            if (r.message) {
                var offerDate = new Date(r.message);
                var appointmentDate = new Date(frm.doc.appointment_date);
                if (appointmentDate < offerDate) {
                   frappe.msgprint(__("Appointment date can't be before offer date"));
                         frappe.validated = false; }               
                        }
                    }
                }); 
},

annexure_template:function(frm){
    if(frm.doc.annexure_template){
        frappe.call({
            method: 'hyde_app.api.get_annexure_template_details',
            args : {
                template : frm.doc.annexure_template
            },
            callback: function(r){
                if(r.message){
                    let message_body = r.message;
                    frm.doc.annexure_components = []
                    for (var i in message_body[1]) {
                        let component = message_body[1][i].component;
                        let amount = message_body[1][i].amount;
                        // Add a new row to the annexure_components table
                        frm.add_child("annexure_components", {
                            component: component,
                            amount: amount
                        });
                    }
                    frm.refresh();
                }
            }

        });
    }
}
})