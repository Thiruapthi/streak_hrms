frappe.ready(function () {
  // Initial message when no Job Opening is selected
  var empty_text_on_page_load = `<b><h5>Please select the <span class="openings">Job Opening</span> Filters for checking status of <span class="openings">Job Applicant</span></h5></b>`;

  // Selectors and initial function call
  var jobApplicant = document.querySelector(".job_applicant");
  var jobApplicantSummaryContainer = document.getElementById(
    "job-applicant-summary-container"
  );
  get_live_job_openings(
    jobApplicant,
    jobApplicantSummaryContainer,
    empty_text_on_page_load
  );

  // Event listener for Job Opening selection change
  jobApplicant.addEventListener("change", function () {
    if (!jobApplicant.value) {
      console.log(jobApplicant.value, "jobApplicant.value if stat");
      // Hide the table and show the initial message when no Job Opening is selected
      $(".job-applicant-table").css({ display: "none" });
      jobApplicantSummaryContainer.innerHTML +=
        '<p style="text-align: center; font-weight: bold;">' +
        empty_text_on_page_load +
        "</p>";
    } else {
      console.log(jobApplicant.value, "jobApplicant.value else stat");
      jobApplicantSummaryContainer.style.display = "";
      // Fetch and render Job Applicant summary based on selected Job Opening
      frappe.call({
        method:
          "hyde_app.www.job_applicant_summary.index.get_job_applicant_summary",
        args: { positions: jobApplicant.value },
        callback: function (response) {
          render_summary(response.message);
        },
      });
    }
  });
});
// Function to fetch live Job Openings and populate the dropdown
function get_live_job_openings(
  jobApplicant,
  jobApplicantSummaryContainer,
  empty_text_on_page_load
) {
  // Show initial message when no Job Opening is selected
  jobApplicantSummaryContainer.innerHTML +=
    '<p style="text-align: center; font-weight: bold;">' +
    empty_text_on_page_load +
    "</p>";

  // Fetch live Job Openings
  frappe.call({
    method: "hyde_app.www.job_applicant_summary.index.get_job_openings",
    callback: function (r) {
      var jobOpenings = r.message;

      // Clear and populate the Job Opening dropdown
      jobApplicant.innerHTML = "";
      var option = document.createElement("option");
      option.text = "Select Job Opening";
      option.value = "";
      jobApplicant.add(option);

      for (var i = 0; i < jobOpenings.length; i++) {
        var option = document.createElement("option");
        option.value = jobOpenings[i].name;
        option.text = jobOpenings[i].name;
        jobApplicant.add(option);
      }
    },
  });
}

// Function to render the Job Applicant summary table
function render_summary(data) {
  console.table(data, "data");
  var container = $("#job-applicant-summary-container");

  if (
    data &&
    data.positions &&
    data.rounds &&
    data.rounds.round_names &&
    data.rounds.applicants
  ) {
    var html = '<table class="job-applicant-table">';
    html +=
      "<thead><tr><th>Position</th><th>Applicant Name</th><th>Status</th>";

    // Dynamic columns based on round names
    data.rounds.round_names.forEach(function (roundName) {
      html += "<th>" + roundName + "</th>";
    });

    html += "</tr></thead>";
    html += "<tbody>";

    // Loop through positions and applicants
    data.positions.forEach(function (position) {
      data.rounds.applicants.forEach(function (applicant) {
        html += "<tr>";
        html += `<td>${position.name} </td>`;
        html += `<td> <a href='/app/job-applicant/${applicant.name}'</a> ${applicant.applicant_name} </td>`;
        html += `<td>${applicant.status}  </td>`;

        // Dynamic columns based on round names
        data.rounds.round_names.forEach(function (roundName) {
          var roundColor = getroundsColor(applicant.rounds_cleared);
          html += `<td><span class='${roundColor}'>${applicant.rounds_cleared}</span></td>`;
        });

        html += "</tr>";
      });
    });

    html += "</tbody></table>";
    container.html(html);
  } else {
    console.error("Data or positions are undefined:", data);
  }
}

// Function to get the color based on rounds cleared status
function getroundsColor(rounds_cleared) {
  switch (rounds_cleared) {
    case "Pending":
      return "indicator-pill orange filterable ellipsis";
    case "Under Review":
      return "indicator-pill blue filterable ellipsis";
    case "Cleared":
      return "indicator-pill green filterable ellipsis";
    case "Rejected":
      return "indicator-pill red filterable ellipsis";
    default:
      return "";
  }
}
