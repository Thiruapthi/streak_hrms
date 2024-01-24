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
        selectedMonth.value = currentMonthStr;

        var currentYear = new Date().getFullYear()
        var currentYearStr = currentYear.toString()

        let selectedYear = document.getElementById('filterByYear');
        selectedYear.value = currentYearStr;


        frappe.call({
            method: "hyde_app.www.monthly_attendance_sheet.index.get_employees",
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
            method: "hyde_app.www.monthly_attendance_sheet.index.get_company_list",
            callback: function (r) {
                var employeeList = r.message
                var selectElement = document.getElementById("filterByCompany");

                for (var i = 0; i < employeeList.length; i++) {
                    var option = document.createElement("option");
                    option.value = employeeList[i].name;
                    option.text = employeeList[i].name
                    selectElement.appendChild(option);
                }

                let filterByCompany = document.getElementById('filterByCompany');
                filterByCompany.value = "Korecent Solutions";
            }
        })

        let defaultMonth = currentMonthStr;
        let employee = 'None'
        let defaultYear = currentYearStr;
        var company = 'None';


        frappe.call({

            method: "hyde_app.www.monthly_attendance_sheet.index.get_monthly_report",
            args: {
                'employee': employee,
                'company': company,
                'year': defaultYear,
                'month': defaultMonth
            },

            callback: function (r) {
                var columns = r.message[0];
                var data = r.message[1];
                var present_date = r.message[2]
                var previous_date = r.message[3]
                displayTableWithData(columns, data, present_date, previous_date)

            }
        });

        document.getElementById('filter').addEventListener('change', applyFilter);
        document.getElementById('filterByYear').addEventListener('change', applyFilter);
        document.getElementById('filterByCompany').addEventListener('change', applyFilter);

        let selectedEmployee = document.getElementById("filterByEmployee")

        selectedEmployee.addEventListener("change", () => {
            fetchCompanyName()
            setTimeout(() => {

                let selectedMonthVal = document.getElementById('filter').value;
                let filterByEmployeeVal = document.getElementById('filterByEmployee').value;
                let filterByYearVal = document.getElementById('filterByYear').value;
                let filterByCompany = document.getElementById('filterByCompany').value;

                frappe.call({

                    method: "hyde_app.www.monthly_attendance_sheet.index.get_monthly_report",
                    args: {
                        'employee': filterByEmployeeVal,
                        'company': filterByCompany,
                        'year': filterByYearVal,
                        'month': selectedMonthVal
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


            let selectedEmployeeVal = selectedEmployee.value

            frappe.call({
                method: "hyde_app.www.monthly_attendance_sheet.index.get_employees",
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


        function applyFilter() {

            let selectedMonthVal = document.getElementById('filter').value;
            let filterByEmployeeVal = document.getElementById('filterByEmployee').value;
            let filterByYearVal = document.getElementById('filterByYear').value;
            let filterByCompany = document.getElementById('filterByCompany').value;


            frappe.call({

                method: "hyde_app.www.monthly_attendance_sheet.index.get_monthly_report",
                args: {
                    'employee': filterByEmployeeVal,
                    'company': filterByCompany,
                    'year': filterByYearVal,
                    'month': selectedMonthVal
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


        function displayTableWithData(columns, data, present_date, previous_date) {
            var table = document.getElementById("data-table");
            while (table.rows.length > 0) {
                table.deleteRow(0); // Deletes the first row in the table
            }

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
                                if (!isNaN(num)) {
                                    if (eachColumn === num) {
                                        if (data[i][`${eachColumn}`] === "P" || data[i][`${eachColumn}`] === "WFH") {

                                            cell.classList.add("present");
                                            cell.innerHTML = data[i][`${eachColumn}`]

                                        } else if (data[i][`${eachColumn}`] === "L") {

                                            cell.classList.add("leave");
                                            cell.innerHTML = data[i][`${eachColumn}`]

                                        } else if (data[i][`${eachColumn}`] === "HD") {

                                            cell.classList.add("half_day");
                                            cell.innerHTML = data[i][`${eachColumn}`]

                                        } else if (data[i][`${eachColumn}`] === "H") {

                                            cell.classList.add("holiday");
                                            cell.innerHTML = data[i][`${eachColumn}`]

                                        } else if (data[i][`${eachColumn}`] === "A") {

                                            cell.classList.add("absent");
                                            cell.innerHTML = data[i][`${eachColumn}`]

                                        }

                                        cell.innerHTML = data[i][`${eachColumn}`]
                                    }
                                } else {

                                    if ((columns[j] === (eachColumn))) {

                                        cell.classList.add("remaining");
                                        cell.innerHTML = data[i][`${eachColumn}`]
                                    }

                                }

                            }
                            else {
                                if ((columns[j] === (eachColumn))) {

                                    cell.classList.add("remaining");
                                    cell.innerHTML = data[i][`${eachColumn}`]


                                }
                            }
                        }
                    }
                }

            }


        }
    }
})