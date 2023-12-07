frappe.ready(function () {
    const isGuest = frappe.session.user === "Guest";

    if (isGuest) {
        const heading = document.getElementById("heading");
        const filter = document.getElementById("filter");
        const filterByEmployee = document.getElementById("filterByEmployee");
        const filterByYear = document.getElementById("filterByYear");
        const filterByCompany = document.getElementById("filterByCompany");
        const applyFiltersButton = document.getElementById("applyFiltersButton");

        heading.textContent = "You can't see the Report without Login";
        heading.classList.add("heading-without-login");
        [filter, filterByEmployee, filterByYear, filterByCompany, applyFiltersButton].forEach(el => el.classList.add("hide-filters"));
    } else {
        const currentMonth = (new Date().getMonth() + 1).toString().padStart(2, '0');
        document.getElementById('filter').value = currentMonth;
        document.getElementById('filterByYear').value = new Date().getFullYear().toString();

        frappe.call({
            method: "hyde_app.www.monthly_attendance_sheet.index.get_employees",
            callback: function (r) {
                populateDropdown("filterByEmployee", r.message);
            }
        });

        frappe.call({
            method: "hyde_app.www.monthly_attendance_sheet.index.get_company_list",
            callback: function (r) {
                populateDropdown("filterByCompany", r.message);
                document.getElementById('filterByCompany').value = "Korecent Solutions";
            }
        });

        const defaultMonth = currentMonth;
        const employee = 'None';
        const defaultYear = new Date().getFullYear().toString();
        const company = 'None';

        fetchMonthlyReport(employee, company, defaultYear, defaultMonth);

        document.getElementById('filter').addEventListener('change', applyFilter);
        document.getElementById('filterByYear').addEventListener('change', applyFilter);
        document.getElementById('filterByCompany').addEventListener('change', applyFilter);

        document.getElementById('filterByEmployee').addEventListener("change", () => {
            fetchCompanyName();
            setTimeout(applyFilter, 1000);
        });

        function fetchMonthlyReport(employee, company, year, month) {
            frappe.call({
                method: "hyde_app.www.monthly_attendance_sheet.index.get_monthly_report",
                args: { 'employee': employee, 'company': company, 'year': year, 'month': month },
                callback: function (r) {
                    const [columns, data, presentDate, previousDate] = r.message;
                    displayTableWithData(columns, data, presentDate, previousDate);
                }
            });
        }

        function applyFilter() {
            const selectedMonthVal = document.getElementById('filter').value;
            const filterByEmployeeVal = document.getElementById('filterByEmployee').value;
            const filterByYearVal = document.getElementById('filterByYear').value;
            const filterByCompany = document.getElementById('filterByCompany').value;

            fetchMonthlyReport(filterByEmployeeVal, filterByCompany, filterByYearVal, selectedMonthVal);
        }

        function displayTableWithData(columns, data, presentDate, previousDate) {
            const table = document.getElementById("data-table");
            clearTable(table);

            if (data.length >= 1) {
                createTableHeader(table, columns);
                createTableBody(table, data, columns);
            }
        }

        function populateDropdown(elementId, list) {
            const selectElement = document.getElementById(elementId);
            list.forEach(item => {
                const option = document.createElement("option");
                option.value = item.name;
                option.text = item.name + ' - ' + item.employee_name || item.name;
                selectElement.appendChild(option);
            });
        }

        function clearTable(table) {
            while (table.rows.length > 0) {
                table.deleteRow(0);
            }
        }

        function createTableHeader(table, columns) {
            const thead = table.createTHead();
            const row = thead.insertRow();
            columns.forEach(column => {
                const th = document.createElement("th");
                th.innerHTML = column;
                row.appendChild(th);
            });
        }

        function createTableBody(table, data, columns) {
            const tbody = table.createTBody();
            data.forEach(rowData => {
                const row = tbody.insertRow();
                columns.forEach(column => {
                    const cell = row.insertCell();
                    for (const key in rowData) {
                        if (column.includes(" ")) {
                            const num = column.split(" ")[0];
                            if (!isNaN(num) && key === num) {
                                applyCellStyle(cell, rowData[key]);
                            } else if (key === column) {
                                applyCellStyle(cell, rowData[key]);
                            }
                        } else if (key === column) {
                            applyCellStyle(cell, rowData[key]);
                        }
                    }
                });
            });
        }

        function applyCellStyle(cell, value) {
            const cellClass = getCellClass(value);
            cell.classList.add(cellClass);
            cell.innerHTML = value;
        }

        function getCellClass(value) {
            switch (value) {
                case "P":
                case "WFH":
                    return "present";
                case "L":
                    return "leave";
                case "HD":
                    return "half_day";
                case "H":
                    return "holiday";
                case "A":
                    return "absent";
                default:
                    return "remaining";
            }
        }

        function fetchCompanyName() {
            const selectedEmployeeVal = document.getElementById("filterByEmployee").value;
            frappe.call({
                method: "hyde_app.www.monthly_attendance_sheet.index.get_employees",
                callback: function (r) {
                    const employeeList = r.message;
                    employeeList.forEach(eachEmployeeItem => {
                        if (eachEmployeeItem.name === selectedEmployeeVal) {
                            document.getElementById("filterByCompany").value = eachEmployeeItem.company;
                        }
                    });
                }
            });
        }
    }
});