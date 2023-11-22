frappe.ui.form.on("Job Applicant", {
  refresh: function (frm) {
    if (!frm.is_new()) {
      frappe.call({
        method: "hrms.hr.doctype.job_applicant.job_applicant.get_interview_details",
        args: {
          job_applicant: frm.doc.name
        },
        callback: function (r) {
          if (r.message) {
            $('.table thead tr').append('<th style="width: 10%"  class="text-left">Interpretation</th>');
            $('.table tbody tr').each(function () {
              var id = $(this).find('td:nth-child(1)').text().trim();
              var interviewData = r.message.interviews[id];
              if (interviewData) {
                var rating = interviewData.average_rating;
                var status = interviewData.status;
                var result = '';

                if (rating === 0 || status === "Pending") {
                  result = '';
                } else {
                  if (rating >= 0 && rating < 1.5) {
                    result = 'Not Acceptable';
                  } else if (rating >= 1.5 && rating < 2.5) {
                    result = 'Poor';
                  } else if (rating >= 2.5 && rating < 3.5) {
                    result = 'Average';
                  } else if (rating >= 3.5 && rating < 4.5) {
                    result = 'Good';
                  } else if (rating >= 4.5 && rating <= 5) {
                    result = 'Exceptional';
                  }
                }
                $(this).append('<td style="width: 10%"  class="text-left">' + result + '</td>');
              } else {
                $(this).append('<td style="width: 10%" class="text-left">No data available</td>');
              }
            });
          }
        }
      });

      frappe.call({
        method: 'hyde_app.api.get_interviewer_details',
        args: {
          job_applicant: frm.doc.name
        },
        callback: function (r) {
          if (r.message) {
            $('.table thead tr').append('<th style="width: 20%" class="text-left">Interviewers</th>');  // Add Interviewers column header
            $('.table tbody tr').each(function () {
              var id = $(this).find('td:nth-child(1)').text().trim();
              var interviewData = r.message.find(data => data.name === id);
              if (interviewData) {
                var interviewerNames = '';
                for (var i = 0; i < interviewData.interviewer_details.length; i++) {
                  interviewerNames += interviewData.interviewer_details[i].custom_interviewer_name + '<br>';
                }
                $(this).append('<td style="width: 20%" class="text-left">' + interviewerNames + '</td>');  // Add Interviewers column
              } else {
                $(this).append('<td style="width: 20%" class="text-left">No data available</td>');  // Add Interviewers column
              }
            });
          }
        }
      });

    }
    function getJobApplications(email, callback) {
      frappe.call({
        args: { email: email },
        method: "hyde_app.api.get_job_applications",
        callback: callback
      });
    }

    if (!frm.is_new()) {
      frm.add_custom_button('Applicant History', function () {
        getJobApplications(frm.doc.email_id, function (r) {
          if (r.message) {
            showJobApplications(r.message);
          }
        });
      });

      getJobApplications(frm.doc.email_id, function (r) {
        if (r.message && r.message.length > 1) {
          $("button:contains('Applicant History')").show();
        } else {
          $("button:contains('Applicant History')").hide();
        }
      });
    }


    cur_frm.events.create_dialog = async function (frm) {
      var interviewRoundsList = []
      await frappe.call({
        args: { job_title: frm.doc.job_title },
        method: "hyde_app.api.get_job_opening_rounds",
        callback: function (r) {
          if (r.message) {
            interviewRoundsList = r.message.custom_round.map(item => item.interview_rounds);
          }
        }
      })
      let d = new frappe.ui.Dialog({
        title: 'Enter Interview Round',
        fields: [
          {
            label: 'Interview Round',
            fieldname: 'interview_round',
            fieldtype: 'Link',
            filters: {
              'name': ['in', interviewRoundsList]
            },
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
  before_save(frm) {
    frappe.call({
      method: 'hyde_app.api.Interview_Rounds',
      args: {
        'job_titles': frm.doc.job_title,
      },
      callback: function (r) {
        cur_frm.clear_table('custom_rounds')
        for (let i = 0; i < r.message.length; i++) {
          frm.add_child('custom_rounds', {
            interview_rounds: r.message[i].interview_rounds,
          });
        }
        cur_frm.refresh_fields('custom_rounds')

      }
    });

  },

  validate(frm) {
    frappe.call({
      method: 'hyde_app.api.create_or_check_contact',
      args: {
        'email': frm.doc.email_id,
        'mobile': frm.doc.phone_number,
        'name': frm.doc.applicant_name
      },
      callback: function (r) {
        if (r.message === 'created') {
          frappe.show_alert({
            message: __('New contact created!'),
            indicator: 'green'
          }, 5);
        } else if (r.message === 'exists') {
          frappe.show_alert({
            message: __('Contact already exists!'),
            indicator: 'orange'
          }, 5);
        } else {
          frappe.show_alert({
            message: __('Error creating or checking contact.'),
            indicator: 'red'
          }, 5);
        }
      }
    });
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
          <td><button class="show-interview-button btn btn-primary" data-target="${item.name
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
