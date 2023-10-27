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
    }
})