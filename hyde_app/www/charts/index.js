frappe.ready(function(){

	var currentMonth = new Date().getMonth() + 1; // Adding 1 to make it 1-12
	
	var currentMonthStr = currentMonth.toString().padStart(2, '0');
	
	let selectedMonth = document.getElementById('filter');
	
	// Set the default selection to the current month
	selectedMonth.value = currentMonthStr;
	frappe.call({
		method: "hyde_app.www.charts.index.get_emplyees",
		callback: function(r) {
			console.log(r)
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
		callback: function(r) {
			console.log(r)
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
	let defaultCompany = 'KCS';
	frappe.call({
		
		method: "hyde_app.www.charts.index.get_script_report_data",
		args: {
			'selectedMonthVal': defaultMonth,  // Pass the selected month as an argument
			'filterByEmployeeVal': defaultEmployee,
			'filterByYearVal': defaultYear,
			'filterByCompany': defaultCompany
		
		},
		
		callback: function(r) {
			console.log(r.message)
			var columns = r.message[0];
			var data = r.message[1];
			// console.log(columns)
			console.log(data)
			// const selectedMonth = document.getElementById('filter').value;
			
			createTable(data,columns)
	
		}
	});
	
	
	function createTable(data,columns){
		var table = document.getElementById("data-table");
		table.innerHTML = '<tr></tr>';
	
		if(data.length>=1){
			
	
			var thead = table.createTHead();
			var row = thead.insertRow();
			for (var i = 0; i < columns.length; i++) {
				var th = document.createElement("th");
	
				th.innerHTML = columns[i].label;
				row.appendChild(th);
			}
	
			//Add table body rows dynamically
			var tbody = table.createTBody();
			for (var i = 0; i < data.length; i++) {
				var row = tbody.insertRow();
				for (var j = 0; j < columns.length; j++) {
					var cell = row.insertCell(j);
	
					if(j==0){
						if(data[i].employee!==undefined){
							cell.innerHTML = data[i].employee
						}
						
					}
					else if(j==1){
						if(data[i].employee_name!==undefined){
						cell.innerHTML = data[i].employee_name
						}
					}
					else if(j==2){
						if(data[i].shift!==undefined){
							cell.innerHTML = data[i].shift
						}
					}
					else{
						cell.innerHTML = data[i][j-2];
	
					}
				}
			}
		}
	
		else{
			var table = document.getElementById('data-table');
			table.innerHTML = '<tr></tr>';
		}
			}		
	document.getElementById('applyFiltersButton').addEventListener('click', applyFilter);
	
	function applyFilter(){
		
		let selectedMonthVal = document.getElementById('filter').value;
		let filterByEmployeeVal = document.getElementById('filterByEmployee').value;
		let filterByYearVal = document.getElementById('filterByYear').value ;
		let filterByCompany = document.getElementById('filterByCompany').value;
			console.log(filterByEmployeeVal)
			console.log(filterByYearVal)
			console.log(filterByCompany)
	
		frappe.call({
			method: "hyde_app.www.charts.index.get_script_report_data",
			args: {
				'selectedMonthVal': selectedMonthVal,  // Pass the selected month as an argument
				'filterByEmployeeVal': filterByEmployeeVal,
				'filterByYearVal': filterByYearVal,
				'filterByCompany': filterByCompany
				
			},
			callback: function(r) {
				console.log(r.message)
				var columns = r.message[0];
				var data = r.message[1];
				// console.log(columns)
				console.log(data)
				// const selectedMonth = document.getElementById('filter').value;
				
				createTable(data,columns)
		
			}
		});
	}
	})
	
	