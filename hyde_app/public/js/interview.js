var firstInterviewMode
frappe.ui.form.on('Interview', {

    refresh: function (frm) {
        frm.fields_dict.interview_details.grid.update_docfield_property('interviewer', "read_only", 1);
        $('[data-fieldtype="Rating"]').css({'pointer-events': 'none','cursor': 'not-allowed'});
        $('button.grid-add-row:contains("Add Row")').on('click', function() {
            $('[data-fieldtype="Rating"]').css({'pointer-events': 'none','cursor': 'not-allowed'});
        });
        if (frm.doc.job_applicant) {
            frappe.db.get_doc("Job Applicant", frm.doc.job_applicant)
                .then((name) => {
                    frm.set_value('custom_exam_portal_link', `https://kcs-ess.frappe.cloud/exam-portal?job_applicant=${name.applicant_name}&applicant_email=${frm.doc.job_applicant}`)
                });
            firstInterviewMode = frm.doc.custom_interview_type
           
        }

    },
    after_save(frm) {
        
        let applicantName = frm.doc.job_applicant;  // Get the name of the saved applicant
        let newStatus// Specify the new status
        if (frm.doc.status === "Cleared") {
            newStatus = frm.doc.interview_round+" Cleared";
        }
        else if (frm.doc.status === "Rejected") {
            newStatus = "Rejected";
        }
        else {
            newStatus = frm.doc.interview_round+" Scheduled";
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
        
        let newInterviewType = frm.doc.custom_interview_type
        if (firstInterviewMode !== newInterviewType){
            sendEmailForChangingInterviewMode(firstInterviewMode, newInterviewType, frm)
        }
    },
    
    scheduled_on: async function(frm){
        if (frm.doc.__islocal) {
            let scheduled_on = frm.doc.scheduled_on
            const currentDate = new Date();
            const formattedDate = currentDate.toISOString().split('T')[0];
            if (scheduled_on < formattedDate){
                const confirmed = await showConfirmationPopup();
                if (!confirmed) {
                    frappe.validated = false;
                }
            }
            
        }
    },

    validate: function(frm){
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
                            frappe.msgprint("You need to clear the previous round - " + previousRoundName);
                            frappe.validated = false;
                        }
                    } else {
                        // No previous rounds to check, allow saving
                        frappe.validated = true;
                    }
                } else {
                    // No previous interview round found, allow saving
                    frappe.validated = true;
                }
            }
        });
    }
})

function showConfirmationPopup() {
    return new Promise(function(resolve, reject) {
        frappe.confirm(
            "The Interview Scheduled Date is Before the Current Date",
            function() {
                resolve(true);
            }
        );
    });
}

function sendEmailForChangingInterviewMode(previousMode, presentMode, frm){
    
    frappe.call({
        method: 'hyde_app.api.sendEmailDuringChangeInterviewMode',
        args: {
            'previous_mode': previousMode,
            'present_mode': presentMode,
            'interview_link': frm.doc.custom_interview_link,
            'interview_address': frm.doc.custom_address,
            'applicant_email': frm.doc.job_applicant,
            'interviewers' : frm.doc.interview_details
        },
        callback: function (r) {
            // console.log(r)
        }
    });
}