// Wait for the DOM to be fully loaded before executing the code
document.addEventListener('DOMContentLoaded', function () {
    // Set the current date in the '.current_date' element using Frappe's utility

    $('.current_date').val(formatDateString(frappe.datetime.get_today()));
    // Make an AJAX call to the server to get the daily attendance report
    frappe.call({
        method: "hyde_app.www.daily_attendance_sheet.index.get_daily_attendance_report",
        callback: function (r) {
            try {
                if (r && r.message) {
                    // Render the attendance table with the received data
                    renderAttendanceTable(r.message);
                } else {
                    console.error("Invalid response from server:", r);
                }
            } catch (error) {
                console.error("Error in rendering table:", error);
            }
        }
    });
});

// Render the attendance table based on the provided data
function renderAttendanceTable(data) {
    // Get the container element to hold the attendance table
    const container = document.getElementById('attendanceTableContainer');

    // Create the table structure
    const table = document.createElement('table');
    const thead = document.createElement('thead');
    const tbody = document.createElement('tbody');

    // Create table header
    const headerRow = document.createElement('tr');
    data[0].forEach(column => {
        const th = document.createElement('th');
        th.textContent = column;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Create table body
    data[1].forEach(row => {
        if (row && typeof row === 'object') {
            const tr = document.createElement('tr');
            Object.values(row).forEach(value => {
                const td = document.createElement('td');
                setCellContent(td, value);
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        } else {
            console.error("Invalid row format:", row);
        }
    });
    table.appendChild(tbody);

    // Apply consistent column widths
    data[0].forEach((_, index) => {
        const col = document.createElement('col');
        col.style.width = '100px'; // Set your preferred width here
        table.appendChild(col);
    });

    // Append the table to the container
    container.appendChild(table);

    // Define itemsPerPage
    const itemsPerPage = 10;

    // Add pagination if needed
    addPagination(data[1].length, itemsPerPage, data[1], tbody);

    // Initial rendering
    showPage(1, itemsPerPage, data[1], tbody);
}

// Add pagination controls if the number of rows exceeds itemsPerPage
function addPagination(totalRows, itemsPerPage, data, tbody) {
    const pageCount = Math.ceil(totalRows / itemsPerPage);

    if (pageCount > 1) {
        const paginationContainer = document.createElement('div');
        paginationContainer.classList.add('pagination-container');

        for (let i = 1; i <= pageCount; i++) {
            const paginationLink = document.createElement('a');
            paginationLink.href = '#';
            paginationLink.textContent = i;
            paginationLink.addEventListener('click', function () {
                showPage(i, itemsPerPage, data, tbody);
                updatePaginationState(paginationContainer, i);
            });
            paginationContainer.appendChild(paginationLink);
        }

        document.getElementById('attendanceTableContainer').appendChild(paginationContainer);
    }
}

// Show the specified page of data
function showPage(page, itemsPerPage, data, tbody) {
    const start = (page - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    const pageData = data.slice(start, end);

    // Clear existing rows
    while (tbody.firstChild) {
        tbody.removeChild(tbody.firstChild);
    }

    // Append new rows
    pageData.forEach(row => {
        if (row && typeof row === 'object') {
            const tr = document.createElement('tr');
            Object.values(row).forEach(value => {
                const td = document.createElement('td');
                setCellContent(td, value);
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        } else {
            console.error("Invalid row format:", row);
        }
    });
}

// Set the content of a table cell based on the value
function setCellContent(td, value) {
    if (value && typeof value === 'object') {
        // If the value is an object, set the content based on its 'value' property
        td.textContent = value.value;
    } else {
        // Set the background color and content based on the value
        td.style.backgroundColor = getBackgroundColor(value);
        td.textContent = value;
    }
}

// Get the background color based on the value
function getBackgroundColor(value) {
    const colorMapping = {
        'Work From Home': 'yellow',
        'Present': 'green',
        'Half Day': 'orange',
        'Absent': 'red',
    };
    return colorMapping[value] || ''; // Default background color
}

// Update the state of the pagination links (active/inactive)
function updatePaginationState(paginationContainer, activePage) {
    paginationContainer.querySelectorAll('a').forEach(link => {
        link.classList.remove('active');
        if (parseInt(link.textContent) === activePage) {
            link.classList.add('active');
        }
    });
}

function formatDateString(dateString) {
    const options = { day: 'numeric', month: 'long', year: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}