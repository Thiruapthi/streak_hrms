frappe.ui.form.on("Job Applicant", {
  refresh: function (frm) {
    
    cur_frm.events.create_dialog = function (frm) {
     
      let d = new frappe.ui.Dialog({
        title: 'Enter Interview Round',
        fields: [
          {
            label: 'Interview Round',
            fieldname: 'interview_round',
            fieldtype: 'Link',
            options: 'Interview Round'
          },
        ],

        primary_action_label: 'Create Interview',
        primary_action(values) {
          frappe.call({
            method: 'hyde_app.api.get_job_applicant_details',
            args: {
              'job_applicant': frm.doc.email_id,
              'job_opening': frm.doc.job_title,
            },
            callback: function (r) {
              if (r.message) {
                const interviewStatus = r.message[0];
                const sourceData = r.message[1];
                const currentRound = values.interview_round;

                const currentRoundIndex = sourceData.findIndex(item => item.interview_rounds === currentRound);

                if (currentRoundIndex > 0) {
                  const previousRoundName = sourceData[currentRoundIndex - 1].interview_rounds;
                  const previousRoundStatus = interviewStatus.find(item => item.interview_round === previousRoundName);

                  if (previousRoundStatus && previousRoundStatus.status === "Cleared") {
                    // Proceed to create the interview
                    frm.events.create_interview(frm, values);
                    d.hide();
                  } else {
                    frappe.msgprint("You need to clear the previous round - " + previousRoundName);
                  }
                } else {
                  // No previous rounds to check, allow creating the interview
                  frm.events.create_interview(frm, values);
                  d.hide();
                }
              } else {
                // No previous interview round found, allow creating the interview
                frm.events.create_interview(frm, values);
                d.hide();
              }
            }
          });
          d.hide();
        }
      });
      d.show();
    }


    var interviewButton = $(".document-link[data-doctype='Interview'] button[data-doctype='Interview']");
    interviewButton.remove();
    const documentTypes = ['Employee', 'Job Offer', 'Employee Onboarding', 'Appointment Letter'];

    documentTypes.forEach((type) => {
      const selector = `.document-link[data-doctype='${type}']`;
      if (frm.doc.status === 'Rejected') {
        $(selector).hide();
        $(".inner-group-button").hide();
      } else {
        $(selector).show();
      }
    });
    frappe.call({
      method: "frappe.client.get_list",
      args: {
        doctype: "Interview",
        filters: {
          job_applicant: frm.doc.name,
        },
      },
      callback: function (response) {
        if (!response.exc) {
          if (response.message.length == 0) {
            $(".document-link[data-doctype='Interview']").hide();
          } else {
            $(".document-link[data-doctype='Interview']").show();
          }
        }
      },
    });

    if (frm.doc.status === "Rejected") {
      var transactionsContainer = document.querySelector('.transactions');
      var formDocumentsContainer = transactionsContainer.querySelector('.form-documents');
      var rowElement = formDocumentsContainer.querySelector('.row');

      rowElement.classList.add('d-flex', 'flex-column');
    }
    else {
      var transactionsContainer = document.querySelector('.transactions');
      var formDocumentsContainer = transactionsContainer.querySelector('.form-documents');
      var rowElement = formDocumentsContainer.querySelector('.row');

      rowElement.classList.remove('d-flex', 'flex-column');
    }

  },
  after_save(frm) {
    // frm.set_value("status", "Interview Pending");
    frappe.call({
      method: 'hyde_app.api.Interview_Rounds',  // Replace with your method and module name
      args: {
        'job_titles': frm.doc.job_title,
        'doc': frm.doc  // Pass any relevant arguments
      },
      callback: function (r) {
        if (!frm.doc.custom_rounds || frm.doc.custom_rounds.length === 0) {
          for (let i = 0; i < r.message.length; i++) {
            let row = frm.add_child('custom_rounds', {
              interview_rounds: r.message[i].interview_rounds,
              qty: 2
            });
          }
          frm.refresh_field('items');
          cur_frm.refresh_fields('rounds')
          frm.save()
        }

      }
    });

  },

  validate(frm) {
    // frm.set_value("status", "Interview Pending");
    if (!frm.doc.contact_created) {
      frappe.call({
        method: 'hyde_app.api.job_applicant_contact',  // Replace with your method and module name
        args: {
          'email': frm.doc.email_id,  // Pass any relevant arguments
          'mobile': frm.doc.phone_number,
          'name': frm.doc.applicant_name
        },
        callback: function (r) {
          cur_frm.refresh_fields('rounds')
          frm.doc.contact_created = 1
          frm.save()
        }
      });
    }
    
	}
})