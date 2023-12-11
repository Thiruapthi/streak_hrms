document.addEventListener('DOMContentLoaded', function () {
    $('.current_date').val(frappe.datetime.get_today());
    frappe.call({
        method: "hyde_app.www.daily_attendance_sheet.index.get_daily_attendance_report",
        callback: function (r) {
            try {
                if (r && r.message) {
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

function renderAttendanceTable(data) {
    const container = document.getElementById('attendanceTableContainer');
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

    // Append the table to the container
    container.appendChild(table);
}

function setCellContent(td, value) {
    if (value && typeof value === 'object') {
        console.log(value,"value")
        td.textContent = value.value;
        
    } else {
        td.style.backgroundColor=getBackgroundColor(value)
        td.textContent = value;
    }
}


function getBackgroundColor(value) {
    const colorMapping = {
        'Work From Home': 'yellow',
        'Present': 'green',
        'Half Day': 'orange',
        'Absent': 'red',
    };
    return colorMapping[value] || ''; // Default background color
}