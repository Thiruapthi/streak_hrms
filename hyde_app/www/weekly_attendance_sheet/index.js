frappe.ready(function () {
	// Add event listeners for start_date and end_date inputs
	document.getElementById('end_date').addEventListener('change', previousdatefiltersFilter);

	// Check if the user is a guest
	if (frappe.session.user === "Guest") {
		const heading = document.getElementById("heading");
		const filtersContainer = document.getElementById("filters-container");
		heading.textContent = "You can't see the Report without Login";
		heading.classList.add("heading-without-login");
		filtersContainer.textContent = "";
	} else {
		// Function to display table data
		function displayTableWithData(columns, data, present_date, previous_date) {
			var table = document.getElementById("data-table");
			var previous_dateEl = document.getElementById("previous_date");
			var present_dateEl = document.getElementById("present_date");
			previous_dateEl.textContent = previous_date;
			present_dateEl.textContent = present_date;

			// Clear existing table rows
			table.innerHTML = "";

			if (data.length >= 1) {
				// Add table header columns dynamically
				var thead = table.createTHead();
				var row = thead.insertRow();
				for (var i = 0; i < columns.length; i++) {
					var th = document.createElement("th");
					th.innerHTML = columns[i];
					row.appendChild(th);
				}

				// Add table body rows dynamically
				var tbody = table.createTBody();
				for (var i = 0; i < data.length; i++) {
					var row = tbody.insertRow();
					for (var j = 0; j < columns.length; j++) {
						var cell = row.insertCell(j);
						for (var eachColumn in data[i]) {
							if (columns[j].includes(" ")) {
								var num = columns[j].split(" ")[0];
								if (!isNaN(num) && eachColumn === num) {
									handleCellStyle(cell, data[i][eachColumn]);
								} else if (columns[j] === eachColumn) {
									handleCellStyle(cell, data[i][eachColumn]);
								}
							} else if (columns[j] === eachColumn) {
								handleCellStyle(cell, data[i][eachColumn]);
							}
						}
					}
				}
			}
		}

		// Set default values
		var defaultCompany = 'Korecent Solutions';
		var defaultEmployee = '';

		// Fetch employee list and populate dropdown
		frappe.call({
			method: "hyde_app.www.weekly_attendance_sheet.index.get_employees",
			callback: function (r) {
				var employeeList = r.message;
				var employeeEl = document.getElementById("employee");
				populateDropdown(employeeEl, employeeList, "name", "employee_name");
			}
		});

		// Fetch company list and populate dropdown
		frappe.call({
			method: "hyde_app.www.weekly_attendance_sheet.index.get_company_list",
			callback: function (r) {
				var companyList = r.message;
				var companyEl = document.getElementById("company");
				populateDropdown(companyEl, companyList, "name", "name");
				companyEl.value = defaultCompany;
			}
		});

		// Fetch and display initial weekly report
		fetchAndDisplayWeeklyReport(defaultEmployee, defaultCompany, document.getElementById('start_date').value, document.getElementById('end_date').value);

		// Event listener for company dropdown change
		document.getElementById('company').addEventListener('change', applyFilter);

		// Event listener for employee dropdown change
		let employeeEl = document.getElementById("employee");
		employeeEl.addEventListener("change", () => {
			fetchCompanyName();
			setTimeout(() => {
				fetchAndDisplayWeeklyReport(employeeEl.value, document.getElementById('company').value, document.getElementById('start_date').value, document.getElementById('end_date').value);
			}, 1000);
		});

		// Function to fetch company name based on selected employee
		function fetchCompanyName() {
			frappe.call({
				method: "hyde_app.www.weekly_attendance_sheet.index.get_employees",
				callback: function (r) {
					var employeeList = r.message;
					for (let eachEmployeeItem of employeeList) {
						if (eachEmployeeItem.name === employeeEl.value) {
							let company = eachEmployeeItem.company;
							var companyEl = document.getElementById("company");
							companyEl.value = company;
						}
					}
				}
			});
		}

		// Function to apply filter
		function applyFilter() {
			let start_date = document.getElementById('start_date').value;
			let end_date = document.getElementById('end_date').value;
			fetchAndDisplayWeeklyReport(employeeEl.value, document.getElementById('company').value, start_date , end_date);
		}

		// Function to handle cell styles based on data value
		function handleCellStyle(cell, value) {
			if (value === "P" || value === "WFH") {
				cell.classList.add("present");
			} else if (value === "L") {
				cell.classList.add("leave");
			} else if (value === "HD") {
				cell.classList.add("half_day");
			} else if (value === "H") {
				cell.classList.add("holiday");
			} else if (value === "A") {
				cell.classList.add("absent");
			}
			cell.innerHTML = value;
		}

		// Function to populate dropdown options
		function populateDropdown(element, dataList, valueField, textField) {
			for (var i = 0; i < dataList.length; i++) {
				var option = document.createElement("option");
				option.value = dataList[i][valueField];
				option.text = dataList[i][valueField] + ' - ' + dataList[i][textField];
				element.appendChild(option);
			}
		}

		// Function to fetch and display weekly report
		function fetchAndDisplayWeeklyReport(employee, company, start_date, end_date) {
			frappe.call({
				method: "hyde_app.www.weekly_attendance_sheet.index.get_weekly_report",
				args: {
					'employee': employee,
					'company': company,
					'start_date_str': start_date,
					'end_date_str': end_date
				},
				callback: function (r) {
					var columns = r.message[0];
					var data = r.message[1];
					var present_date = r.message[2];
					var previous_date = r.message[3];
					displayTableWithData(columns, data, present_date, previous_date);
				}
			});
		}
	}

	function previousdatefiltersFilter() {
		let employeeVal = document.getElementById('employee').value;
		let companyVal = document.getElementById('company').value;
		let start_date = document.getElementById('start_date').value;
		let end_date = document.getElementById('end_date').value;

		fetchAndDisplayWeeklyReport(employeeVal, companyVal, start_date, end_date);
	}
});