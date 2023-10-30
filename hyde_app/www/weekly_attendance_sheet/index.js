frappe.ready(function(){

	if(frappe.session.user === "Guest"){
		const heading = document.getElementById("heading")
		const filtersContainer = document.getElementById("filters-container")
		heading.textContent = "You can't see the Report without Login"
		heading.classList.add("heading-without-login")
		filtersContainer.textContent = ""
		

	}
	else{

		function displayTableWithData(columns, data, present_date, previous_date) {
			var table = document.getElementById("data-table");
			var previous_dateEl = document.getElementById("previous_date");
			var present_dateEl = document.getElementById("present_date");
			previous_dateEl.textContent = previous_date;
			present_dateEl.textContent = present_date;
			while (table.rows.length > 0) {
				table.deleteRow(0); // Deletes the first row in the table
			}

			// Add table header columns dynamically
			var thead = table.createTHead();
			var row = thead.insertRow();
			for (var i = 0; i < columns.length; i++) {
				var th = document.createElement("th");
				th.innerHTML = columns[i].label;
				row.appendChild(th);
			}
		
			// Add table body rows dynamically
			var tbody = table.createTBody();
			for (var i = 0; i < data.length; i++) {
				var row = tbody.insertRow();
				for (var j = 0; j < columns.length; j++) {
					var cell = row.insertCell(j);
		
					for(var eachColumn in data[i]){
		
						if(columns[j].fieldname===parseInt(eachColumn)){
							if(data[i][`${eachColumn}`]==="P" || data[i][`${eachColumn}`]==="WFH"){
							
								cell.classList.add("present");
								cell.innerHTML = data[i][`${eachColumn}`]
		
							}else if(data[i][`${eachColumn}`]==="L"){
		
								cell.classList.add("leave");
								cell.innerHTML = data[i][`${eachColumn}`]
		
							}else if(data[i][`${eachColumn}`]==="HD"){
		
								cell.classList.add("half_day");
								cell.innerHTML = data[i][`${eachColumn}`]
		
							}else if(data[i][`${eachColumn}`]==="H"){
		
								cell.classList.add("holiday");
								cell.innerHTML = data[i][`${eachColumn}`]
		
							}else if(data[i][`${eachColumn}`]==="A"){
		
								cell.classList.add("absent");
								cell.innerHTML = data[i][`${eachColumn}`]
		
							}
		
							cell.innerHTML = data[i][`${eachColumn}`]
						}
						else{
							if((columns[j].fieldname===(eachColumn))){
		
								cell.classList.add("remaining");
								cell.innerHTML = data[i][`${eachColumn}`]
		
		
							}
							
		
						}
					}
				}
			}
		}


		var defaultCompany = 'Korecent Solutions';
		var defaultEmployee = '';
		
		frappe.call({
			method: "hyde_app.www.weekly_attendance_sheet.index.get_employees",
			callback: function (r) {
				var employeeList = r.message
				var employeeEl = document.getElementById("employee");

				for (var i = 0; i < employeeList.length; i++) {
					var option = document.createElement("option");
					option.value = employeeList[i].name;
					option.text = employeeList[i].name + ' - ' + employeeList[i].employee_name;
					employeeEl.appendChild(option);
				}
			}
		})

		frappe.call({
			method: "hyde_app.www.weekly_attendance_sheet.index.get_company_list",
			callback: function (r) {
				var employeeList = r.message
				var companyEl = document.getElementById("company");

				for (var i = 0; i < employeeList.length; i++) {
					var option = document.createElement("option");
					option.value = employeeList[i].name;
					option.text = employeeList[i].name
					companyEl.appendChild(option);
				}

		    var companyEl = document.getElementById('company');
		    companyEl.value = defaultCompany;
			}
		})		

		frappe.call({

			method: "hyde_app.www.weekly_attendance_sheet.index.get_weekly_report",
			args: {
				
				'employee': defaultEmployee,
				'company': defaultCompany

			},

			callback: function (r) {
				var columns = r.message[0];
				var data = r.message[1];
				var present_date = r.message[2]
				var previous_date = r.message[3]							
				displayTableWithData(columns, data, present_date, previous_date)
		
			}
		});
		
		document.getElementById('company').addEventListener('change', applyFilter);

		let employeeEl = document.getElementById("employee")

		employeeEl.addEventListener("change", () => {
			fetchCompanyName()
			setTimeout(() => {

				let employeeVal = document.getElementById('employee').value;
				let companyVal = document.getElementById('company').value;
				
				frappe.call({
					method: "hyde_app.www.weekly_attendance_sheet.index.get_weekly_report",
					args: {
						'employee': employeeVal,
						'company': companyVal
					},
					callback: function (r) {
						var columns = r.message[0];
						var data = r.message[1];
						var present_date = r.message[2]
						var previous_date = r.message[3]							
						displayTableWithData(columns, data, present_date, previous_date)
					}
				});

			}, 1000);


		})

		function fetchCompanyName() {

			frappe.call({
				method:"hyde_app.www.weekly_attendance_sheet.index.get_employees",
				callback: function (r) {
					var employeeList = r.message
					
					for (let eachEmployeeItem of employeeList) {
						if (eachEmployeeItem.name === employeeEl.value) {
							let company = eachEmployeeItem.company

							var companyEl = document.getElementById("company")
							companyEl.value = company
						}
					}

				}
			})

		}
		
		function applyFilter() {

			let employeeVal = document.getElementById('employee').value;
			let companyVal = document.getElementById('company').value;

			frappe.call({
				method: "hyde_app.www.weekly_attendance_sheet.index.get_weekly_report",
				args: {
					'employee': employeeVal,
					'company': companyVal
				},
				callback: function (r) {
					var columns = r.message[0];
					var data = r.message[1];
					var present_date = r.message[2]
					var previous_date = r.message[3]							
					displayTableWithData(columns, data, present_date, previous_date)
					
				}
			});
		}

	}
	

});
