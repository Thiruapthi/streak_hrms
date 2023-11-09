frappe.ui.form.on("Job Applicant", {
  refresh: function (frm) {
    frm.add_custom_button('Applicant History', function(){
      frappe.call({
        args: {email:frm.doc.email_id},
        method: "hyde_app.api.get_job_applications",
        callback: function(r) {
          if (r.message) {
            showJobApplications(r.message);
        }  }
    });
    });
    
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


function showJobApplications(data) {
  console.log(data);
  let d = new frappe.ui.Dialog({
    title: "Job Applications",
    fields: [
      {
        label: "Job Applications",
        fieldname: "history",
        fieldtype: "HTML",
        options: createItemTable(data),
        read_only: 1,
      },
    ],
    size: "large",
    primary_action_label: "Submit",
    primary_action: function (values) {
      console.log(values);
      d.hide();
    },
  });

  d.show();
  setTimeout(function () {
    data.forEach((item) => {
      if (item.interviews.length === 0) {
        console.log(item.name, "test");

        $(`button[data-target="${item.name}"]`).hide();
      }
    });
  }, 500);
}

function createItemTable(data) {
  let tableHTML = `
      <table class="table table-striped table-hover">
        <thead class="thead-dark">
          <tr>
            <th class="table-heading">#</th>
            <th class="table-heading">Applicant Name</th>
            <th class="table-heading">Job Title</th>
            <th class="table-heading">Status</th>
            <th class="table-heading">Applicant Rating</th>
            <th class="table-heading">Interview Feedback</th>
          </tr>
        </thead>
        <tbody>
    `;

  data.forEach((item, index) => {
    tableHTML += `
        <tr>
          <td>${index + 1}</td>
          <td>${item.applicant_name}</td>
          <td>${item.job_title}</td>
          <td>${item.status}</td>
          <td>${item.applicant_rating}</td>
          <td><button class="show-interview-button btn btn-primary" data-target="${
            item.name
          }">Show</button></td>
        </tr>
        <tr id="${item.name}" style="display: none;">
          <td colspan="6">
            <table class="interview-table">
              <thead>
                <tr>
                  <th>Interview Round</th>
                  <th>Interviewer</th>
                  <th>Result</th>
                  <th>Feedback</th>
                </tr>
              </thead>
              <tbody>
                ${item.interviews
                  .map(
                    (interview) => `
                      <tr>
                        <td>${interview.interview_round}</td>
                        <td>${interview.interviewer}</td>
                        <td>${interview.result}</td>
                        <td>${interview.feedback}</td>
                      </tr>
                    `
                  )
                  .join("")}
              </tbody>
            </table>
          </td>
        </tr>
      `;
  });

  tableHTML += `
        </tbody>
      </table>
    `;

  return tableHTML;
}

$(document).on("click", ".show-interview-button", function () {
  const target = $(this).data("target");
  var trElement = document.getElementById(target);

  if (trElement) {
    if (trElement.style.display === "none" || trElement.style.display === "") {
      trElement.style.display = "table-row";
    } else {
      trElement.style.display = "none";
    }
  }
});
