frappe.ui.form.on('Interview', {
    after_save(frm) {
        let applicantName = frm.doc.job_applicant;  // Get the name of the saved applicant
        let newStatus// Specify the new status
        if (frm.doc.status === "Cleared") {
            newStatus = "Job Offer Pending";
        }
        else if(frm.doc.status === "Rejected"){
            newStatus = "Rejected";
        }
        else {
            newStatus = 'Interview Scheduled'
        }
        frappe.call({
            method: 'hyde_app.api.update_applicant_status_interview',
            args: {
                'applicant_name': applicantName,
                'status': newStatus
            },
            callback:function(r){
                frappe.realtime.on("applicant_status_update", function(data) {
                    console.log('Status updated:', data.applicant_name, data.status,data.doc);
                    let frm = data.doc
                    frm.refresh()

                });
            }
        });
    }
})