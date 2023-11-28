frappe.ready(function () {
  const jo_filter = $(".job_applicant");
  const jobApplicantSummaryContainer = $("#job-applicant-summary-container");

  // Initial message when no Job Opening is selected
  const emptyTextOnPageLoad = `<b><h5>Please select the <span class="openings">Job Opening</span> Filters for checking status of <span class="openings">Job Applicant</span></h5></b>`;

  // Function to fetch live Job Openings and populate the dropdown
  function getLiveJobOpenings() {
    frappe.call({
      method: "hyde_app.www.job_applicant_summary.index.get_job_openings",
      callback: function (response) {
        const jobOpenings = response.message;
        jo_filter.html(`<option value="">Select Job Opening</option>${jobOpenings.map(o => `<option value="${o.name}">${o.name}</option>`).join('')}`);
      },
    });
  }

  // Event listener for Job Opening selection change
  jo_filter.on("change", function () {
    const selectedJobOpening = jo_filter.val();

    if (!selectedJobOpening) {
      // Hide the table and show the initial message when no Job Opening is selected
      $(".job-applicant-table").hide();
      jobApplicantSummaryContainer.html(`<p style="text-align: center; font-weight: bold;">${emptyTextOnPageLoad}</p>`);
    } else {
      // Fetch and render Job Applicant summary based on selected Job Opening
      frappe.call({
        method: "hyde_app.www.job_applicant_summary.index.get_job_applicant_summary",
        args: { positions: selectedJobOpening },
        callback: function (response) {
          if (response.message.data == "No data found") {
            $(".job-applicant-table").hide();
            frappe.show_alert({
              message: __(`<b>There is no specific information with position name <span class="openings">${selectedJobOpening}</span></b>`),
              indicator: "red",
            }, 5);
          } else {
            renderSummary(response.message, selectedJobOpening);
          }
        },
      });
    }
  });

  // Fetch live Job Openings on page load
  getLiveJobOpenings();
});

// Function to render the Job Applicant summary table
function renderSummary(data, positions) {
  const container = $("#job-applicant-summary-container");
  const { interview_details } = data;

  if (interview_details && interview_details.round_names && interview_details.applicants) {
    const html = `
      <table class="job-applicant-table">
        <thead>
          <tr>
            <th>Position</th>
            <th>Applicant Name</th>
            <th>Status</th>
            ${interview_details.round_names.map(roundName => `<th>${roundName}</th>`).join('')}
          </tr>
        </thead>
        <tbody>
          ${interview_details.applicants.map(applicant => `
            <tr>
              <td>${positions}</td>
              <td><a href='/app/job-applicant/${applicant.name}'>${applicant.applicant_name}</a></td>
              <td>${applicant.status}</td>
              ${interview_details.round_names.map(roundName => {
      const roundCleared = Array.isArray(applicant.rounds_cleared)
        ? applicant.rounds_cleared.find(entry => entry.interview_round === roundName)
        : applicant.rounds_cleared && applicant.rounds_cleared.interview_round === roundName
          ? applicant.rounds_cleared
          : null;

      const roundColor = roundCleared ? getroundsColor(roundCleared.status) : '';
      const status = roundCleared ? roundCleared.status : 'N.A';
      return `<td><span class='${roundColor}'>${status}</span></td>`;
    }).join('')}
            </tr>`).join('')}
        </tbody>
      </table>`;

    container.html(html).show();
  } else {
    console.error("Data or positions are undefined:", data);
  }
}

// Function to get the color based on rounds cleared status
function getroundsColor(roundsCleared) {
  switch (roundsCleared) {
    case "Pending": return "indicator-pill orange filterable ellipsis";
    case "Under Review": return "indicator-pill blue filterable ellipsis";
    case "Cleared": return "indicator-pill green filterable ellipsis";
    case "Rejected": return "indicator-pill red filterable ellipsis";
    default: return "";
  }
}
