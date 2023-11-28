frappe.ui.form.on('Interview', {
    refresh(frm) {
        let applicantName = frm.doc.job_applicant;  // Get the name of the saved applicant
        let newStatus// Specify the new status
        if (frm.doc.status === "Cleared") {
            newStatus = "Job Offer Pending";
        }
        else if (frm.doc.status === "Rejected") {
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
            callback: function (r) {
                // location.reload();
            }
        });
    },

    validate(frm) {
        frappe.call({
            method: 'hyde_app.api.get_job_applicant_details',
            args: {
                'job_applicant': frm.doc.job_applicant,
                'job_opening': frm.doc.job_opening,
            },
            callback: function (r) {
                if (r.message) {
                    const interviewStatus = r.message[0];
                    const sourceData = r.message[1];
                    const currentRound = frm.doc.interview_round;
    
                    const currentRoundIndex = sourceData.findIndex(item => item.interview_rounds === currentRound);
                  
                    if (currentRoundIndex > 0) {
                        const previousRoundName = sourceData[currentRoundIndex - 1].interview_rounds;
                        const previousRoundStatus = interviewStatus.find(item => item.interview_round === previousRoundName);
    
                        if (previousRoundStatus && previousRoundStatus.status === "Cleared") {
                            frappe.validated = true;
                        } else {
                            frappe.msgprint("You need to clear the previous round - "+previousRoundName);
                            frappe.validated = false;
                        }
                    }   else {
                        // No previous rounds to check, allow saving
                        frappe.validated = true;
                    }
                }else {
                // No previous interview round found, allow saving
                 frappe.validated = true;
                }
            }
        });
    }
})