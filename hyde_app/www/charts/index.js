frappe.ready(function () {
	if (frappe.session.user === "Guest") {
		const heading = document.getElementById("heading")
		const filter = document.getElementById("filter")
		const filterByEmployee = document.getElementById("filterByEmployee")
		const filterByYear = document.getElementById("filterByYear")
		const filterByCompany = document.getElementById("filterByCompany")
		const applyFiltersButton = document.getElementById("applyFiltersButton")

		heading.textContent = "You can't see the Report without Login"
		heading.classList.add("heading-without-login")
		filter.classList.add("hide-filters")
		filterByEmployee.classList.add("hide-filters")
		filterByYear.classList.add("hide-filters")
		filterByCompany.classList.add("hide-filters")
		applyFiltersButton.classList.add("hide-filters")

	}
	else {

		var currentMonth = new Date().getMonth() + 1; // Adding 1 to make it 1-12

		var currentMonthStr = currentMonth.toString().padStart(2, '0');

		let selectedMonth = document.getElementById('filter');

		// Set the default selection to the current month
		selectedMonth.value = currentMonthStr;


		frappe.call({
			method: "hyde_app.www.charts.index.get_employees",
			callback: function (r) {
				var employeeList = r.message
				var selectElement = document.getElementById("filterByEmployee");

				for (var i = 0; i < employeeList.length; i++) {
					var option = document.createElement("option");
					option.value = employeeList[i].name;
					option.text = employeeList[i].name + ' - ' + employeeList[i].employee_name;
					selectElement.appendChild(option);
				}

			}
		})
		frappe.call({
			method: "hyde_app.www.charts.index.get_company_list",
			callback: function (r) {
				var employeeList = r.message
				var selectElement = document.getElementById("filterByCompany");

				for (var i = 0; i < employeeList.length; i++) {
					var option = document.createElement("option");
					option.value = employeeList[i].name;
					option.text = employeeList[i].name
					selectElement.appendChild(option);
				}

			}
		})
		let defaultMonth = currentMonthStr;
		let defaultEmployee = 'None'
		let defaultYear = '2023'
		let defaultCompany = 'Korecent Solutions'
		// let filterByCompany = document.getElementById('filterByCompany')
		// filterByCompany.value = defaultCompany


		frappe.call({

			method: "hyde_app.www.charts.index.get_script_report_data",
			args: {
				'selectedMonthVal': defaultMonth,  // Pass the selected month as an argument
				'filterByEmployeeVal': defaultEmployee,
				'filterByYearVal': defaultYear,
				'filterByCompany': defaultCompany

			},

			callback: function (r) {
				var columns = r.message[0];
				var data = r.message[1];

				createTable(data, columns)

			}
		});


		let selectedEmployee = document.getElementById("filterByEmployee")


		selectedEmployee.addEventListener("change", () => {
			fetchCompanyName()
			setTimeout(() => {

				let selectedMonthVal = document.getElementById('filter').value;
				let filterByEmployeeVal = document.getElementById('filterByEmployee').value;
				let filterByYearVal = document.getElementById('filterByYear').value;
				let filterByCompany = document.getElementById('filterByCompany').value;


				frappe.call({
					method: "hyde_app.www.charts.index.get_script_report_data",
					args: {
						'selectedMonthVal': selectedMonthVal,  // Pass the selected month as an argument
						'filterByEmployeeVal': filterByEmployeeVal,
						'filterByYearVal': filterByYearVal,
						'filterByCompany': filterByCompany

					},
					callback: function (r) {
						var columns = r.message[0];
						var data = r.message[1];

						createTable(data, columns)

					}
				});

			}, 1000);


		})

		function fetchCompanyName() {


			let selectedEmployeeVal = selectedEmployee.value

			frappe.call({
				method: "hyde_app.www.charts.index.get_employees",
				callback: function (r) {
					var employeeList = r.message


					for (let eachEmployeeItem of employeeList) {
						if (eachEmployeeItem.name === selectedEmployeeVal) {
							let company = eachEmployeeItem.company

							let selectedCompany = document.getElementById("filterByCompany")
							selectedCompany.value = company
						}
					}

				}
			})

		}

		function createTable(data, columns) {
			var table = document.getElementById("data-table");
			table.innerHTML = '<tr></tr>';

			if (data.length >= 1) {
				var thead = table.createTHead();
				var row = thead.insertRow();

				for (var i = 0; i < columns.length; i++) {
					if (columns[i].label !== "Shift") {
						var th = document.createElement("th");
						th.innerHTML = columns[i].label;
						row.appendChild(th);
					}
				}

				// Add table body rows dynamically
				var tbody = table.createTBody();
				for (var i = 0; i < data.length; i++) {
					var row = tbody.insertRow();

					for (var j = 0; j < columns.length; j++) {
						if (columns[j].label !== "Shift") {
							var cell = row.insertCell(row.cells.length);

							if (j == 0) {
								if (data[i].employee !== undefined) {
									cell.innerHTML = data[i].employee;
								}
							} else if (j == 1) {
								if (data[i].employee_name !== undefined) {
									cell.innerHTML = data[i].employee_name;
								}
							} else {
								cell.innerHTML = data[i][j - 2];
							}
						}
					}
				}
			}
			else {
				var table = document.getElementById('data-table');
				table.innerHTML = '<tr></tr>';
			}
		}


		document.getElementById('filter').addEventListener('change', applyFilter);
		document.getElementById('filterByYear').addEventListener('change', applyFilter);
		document.getElementById('filterByCompany').addEventListener('change', applyFilter);


		function applyFilter() {

			let selectedMonthVal = document.getElementById('filter').value;
			let filterByEmployeeVal = document.getElementById('filterByEmployee').value;
			let filterByYearVal = document.getElementById('filterByYear').value;
			let filterByCompany = document.getElementById('filterByCompany').value;

			frappe.call({
				method: "hyde_app.www.charts.index.get_script_report_data",
				args: {
					'selectedMonthVal': selectedMonthVal,  // Pass the selected month as an argument
					'filterByEmployeeVal': filterByEmployeeVal,
					'filterByYearVal': filterByYearVal,
					'filterByCompany': filterByCompany

				},
				callback: function (r) {
					var columns = r.message[0];
					var data = r.message[1];

					createTable(data, columns)

				}
			});
		}
	}
})

