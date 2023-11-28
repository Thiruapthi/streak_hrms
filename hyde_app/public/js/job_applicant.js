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

            $('.table thead tr').append('<th style="width: 20%" class="text-left">Interviewers</th>');  // Add Interviewers column header
            $('.table tbody tr').each(function () {
              var id = $(this).find('td:nth-child(1)').text().trim();
                const filters = {
                    "parent": id,
                    "parenttype": "Interview",
                    'parentfield':'interview_details'
                };
            
                frappe.db.get_list("Interview Detail", {fields: ['*'], filters: filters})
                .then(interviewData => {
                  if (interviewData.length > 0) {
                    var interviewerNames = '';
                    for (var i = 0; i < interviewData.length; i++) {                 
                        interviewerNames += interviewData[i].custom_interviewer_name + '<br>';
                      
                    }
                    $(this).append('<td style="width: 20%" class="text-left">' + interviewerNames + '</td>');  // Add Interviewers column
                  } else {
                      $(this).append('<td style="width: 20%" class="text-left">No data available</td>');  // Add Interviewers column
                    }
                })
              })
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
            displayJobApplications(r.message);
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
  job_title(frm) {
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


// Display job applications in a dialog
function displayJobApplications(data) {
  // Create a dialog to show job applications
  const dialog = new frappe.ui.Dialog({
      title: "Job Applications",
      fields: [
          {
              label: "Job Applications",
              fieldname: "history",
              fieldtype: "HTML",
              options: createJobApplicationTable(data),
              read_only: 1,
          },
      ],
      size: "large",
      primary_action_label: "Okay",
      primary_action: function (values) {
          dialog.hide();
          location.reload();
      },
  });

  dialog.show();
  setTimeout(function () {
      // Update status indicators
      updateStatusIndicators();
      // Hide interview details (eye icon) if no interviews exist
      hideNoInterviewDetails(data);
  }, 500);
}

// Create the job application table HTML
function createJobApplicationTable(data) {
  let tableHTML = `
  <table class="table">
    <thead >
      <tr>
        <th scope="col">#</th>
        <th scope="col">Applicant Name</th>
        <th scope="col">Job Title</th>
        <th scope="col">Status</th>
        <th scope="col">Summary</th>
      </tr>
    </thead>
    <tbody>
`;

  data.forEach((item, index) => {
      tableHTML += `
    <tr>
      <td scope="row">${index + 1}</td>
      <td>${item.applicant_name}</td>
      <td>${item.job_title}</td>
      <td><span class="indicator-pill whitespace-nowrap white status-indicator">${item.status}</span></td>
      <td style="display: flex;text-align: center;align-items: center;justify-content: space-around;"><i class="show-interview-button fa fa-eye-slash" data-target="${item.name}" style="color: black; cursor: pointer;"></i><p class="open-new-tab" data-value="/app/job-applicant/${item.name}"  style="margin: 0; font-size: 20px; cursor: pointer;">&#8594;</p></td>    
    </tr>
    <tr id="${item.name}" style="display: none;">
      <td colspan="6">
        <table class="interview-table table table-bordered table-striped">
          <thead class="thead-dark">
            <tr>
            <th scope="col">#</th>
              <th scope="col">Interview</th>
              <th scope="col">Interview Round</th>
              <th scope="col">Date</th>
              <th scope="col">Status</th>
              <th scope="col">Rating</th>
              <th scope="col">Action</th>
            </tr>
          </thead>
          <tbody>
            ${Object.keys(item.interview_summary.interviews).length > 0 ?
              Object.values(item.interview_summary.interviews)
                  .map((interview, interviewIndex) => `
                  <tr>
                  <td>${interviewIndex + 1}</td>
                  <td class="clickable-name" data-name="${interview["name"]}">${interview["name"]}</td>
                  <td>${interview["interview_round"]}</td>
                    <td>${frappe.datetime.str_to_user(interview["scheduled_on"])}</td>
                    <td><span class="indicator-pill whitespace-nowrap white status-indicator">${interview["status"]}</span></td>
                    <td>${interview["average_rating"]}</td>
                    <td style="display: flex;text-align: center;align-items: center;justify-content: space-around;">
                    <p class="open-new-tab" data-value="/app/interview/${interview["name"]}"  style="margin: 0; font-size: 20px; cursor: pointer;">&#8594;</p>
                    </td>
                  </tr>
                `)
                  .join("")
              : '<tr><td colspan="3">No interviews available</td></tr>'
          }
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


// Function to fetch and display Interview feedback data
function showFeedbackOnHover(interviewName, targetElement) {
  frappe.call({
      method: 'hyde_app.api.get_interview_feedback',
      args: {
          'interview_name': interviewName,
      },
      callback: function (r) {
          const feedbackData = r.message;
          let feedbackHTML = '<div class="feedback-container" style="font-family: Arial, sans-serif; font-size: 14px;">'; // Container for feedback
          let indicatorClass = 'white'; // Default class
          // Loop through each feedback record and create HTML
          feedbackData.forEach((feedback) => {
              // Apply different classes based on feedback.result value
              switch (feedback.result) {
                  case 'Cleared':
                      indicatorClass = 'green';
                      break;
                  case 'Rejected':
                      indicatorClass = 'red';
                      break;
                  case 'Under Review':
                      indicatorClass = 'blue';
                      break;
                  default:
                      break;
              }
              feedbackHTML += `<p style="margin-bottom: 10px;">
                                    <span style="font-weight: bold; cursor: pointer">${feedback.name}</span>
                                    <i class="fa fa-external-link" style="margin-left: 5px;"></i>
                                    <br>
                                    Interviewer: ${feedback.interviewer}<br> 
                                    <strong class="indicator-pill whitespace-nowrap status-indicator ${indicatorClass}" style="padding: 5px; border-radius: 5px; color: #fff; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); background-color: #555;">${feedback.result}</strong>
                                </p> `;
              feedbackHTML += '<hr style="border-top: 1px solid #ddd;">';
          });

          feedbackHTML += '</div>'; // Close the container

          $(targetElement).popover({
              trigger: 'manual',
              placement: 'right',
              html: true,
              content: feedbackHTML,
          });

          // Show the popover
          $(targetElement).popover('show');

          $('.feedback-container p:contains("Interviewer:")').click(function () {
              const feedbackName = $(this).find('span').text();
              window.open(`${window.location.origin}/app/interview-feedback/${feedbackName}`, '_blank');
          }).css({
              'cursor': 'pointer',
              'transition': 'background-color 0.3s ease',
              'padding': '10px',
              'border-radius': '5px',
              'box-shadow': '2px 2px 5px rgba(0,0,0,0.2)',
              'margin-bottom': '15px'
          }).hover(function () {
              $(this).css({
                  'background-color': '#f0f0f0'
              });
          }, function () {
              $(this).css({
                  'background-color': 'transparent'
              });
          });

          // Event listener for hovering over the interviewer's name in the feedback list
          $('.feedback-container p:contains("Interviewer:")').hover(function () {
              const feedbackName = $(this).find('span').text();
              const filteredData = feedbackData.filter(item => item.name === feedbackName);
              let skillAssessmentHTML = '<ul style="list-style-type: none; padding-left: 0;">';

              filteredData[0].skill_assessment.forEach((assessment) => {
                  skillAssessmentHTML += `
                    <li style="margin-bottom: 8px; color: #333; border-bottom: 1px solid #ccc; padding-bottom: 5px;">
                        <strong>${assessment.idx}. </strong> ${assessment.skill} - ${assessment.rating === 0
                          ? 0
                          : assessment.rating === 0.2
                              ? 1
                              : assessment.rating === 0.4
                                  ? 2
                                  : assessment.rating === 0.6
                                      ? 3
                                      : assessment.rating === 0.8
                                          ? 4
                                          : assessment.rating === 1
                                              ? 5
                                              : 'N/A'
                      }
                    </li>
                `;
              });

              skillAssessmentHTML += '</ul>';

              $(this).popover({
                  trigger: 'manual',
                  placement: 'right',
                  content: skillAssessmentHTML,
                  html: true
              });
              $(this).popover('show');
          }, function () {
              $(this).popover('hide');
          });


      }
  });
}

// Function to update status indicators based on data-status attribute
function updateStatusIndicators() {
  $('.status-indicator').each(function () {
      const status = $(this).text().trim();
      switch (status) {
          case 'Open':
          case 'Replied':
          case 'Interview Pending':
          case 'Job Offer Pending':
              $(this).removeClass('white').addClass('orange');
              break;
          case 'Rejected':
          case 'Hold':
          case 'Pending':
          case 'Job Offer Rejected':
              $(this).removeClass('white').addClass('red');
              break;
          case 'Appointment Letter Released':
          case 'Employee Onboarding In Progress':
          case 'Interview Scheduled':
          case 'Job Offer Released':
          case 'Job Offer Accepted':
          case 'Applicant Onboarded':
              $(this).removeClass('white').addClass('gray');
              break;
          case 'Accepted':
          case 'Cleared':
              $(this).removeClass('white').addClass('green');
              break;
          case 'Under Review':
              $(this).removeClass('white').addClass('blue');
              break;
          default:
              break;
      }
  });
}

// Function to hide interview details if no interviews exist
function hideNoInterviewDetails(data) {
  data.forEach((item) => {;
      if (Object.keys(item.interview_summary.interviews).length === 0) {
          $(`i[data-target="${item.name}"]`).hide();
      }
  });
}



// Event listeners

$(document).on("click", ".show-interview-button", function () {
  const target = $(this).data("target");
  const trElement = document.getElementById(target);
  if (trElement) {
      if (trElement.style.display === "none") {
          trElement.style.display = "table-row";

          $(this).removeClass('fa-eye-slash').addClass('fa-eye');
      } else {
          trElement.style.display = "none";
          $(this).removeClass('fa-eye').addClass('fa-eye-slash');
      }
  }
});

$(document).on("mouseenter", ".clickable-name", function () {
  $('.clickable-name').not(this).popover('hide');
  const interviewName = $(this).data("name");
  const targetElement = this;
  // Fetch and display feedback data on hover
  showFeedbackOnHover(interviewName, targetElement);
});

$(document).on('click', '.open-new-tab', function (event) {
  event.preventDefault();
  const value = $(this).data('value');
  const baseOrigin = window.location.origin;

  if (value) {
      const url = baseOrigin + value;
      window.open(url, '_blank');
  } else {
      console.error('No value found to open a new tab.');
  }
});

$(document).on('click', function (e) {
  if (!$(e.target).hasClass('clickable-name') && $(e.target).closest('.popover').length === 0) {
      $('.clickable-name').popover('hide');
  }
});
