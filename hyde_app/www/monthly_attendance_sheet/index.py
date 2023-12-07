import frappe
from frappe import _
from datetime import date, timedelta
from collections import defaultdict


@frappe.whitelist(allow_guest=True)
def get_monthly_report(company, employee, year, month):
    year = int(year)
    month = int(month)

    # Calculate the first and last day of the specified month and year
    first_day_of_month = date(year, month, 1)

    # Handle the case where the month is December (12)
    if month == 12:
        last_day_of_month = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day_of_month = date(year, month + 1, 1) - timedelta(days=1)
        

    columns = ["Employee", "Employee Name"]

    # Loop through the days of the month
    for day in range(1, last_day_of_month.day + 1):
        date_obj = date(year, month, day)
        columns.append(f"{day} {date_obj.strftime('%a')}")

    # Fetch attendance records
    records = fetch_attendance_records(company, employee, first_day_of_month, last_day_of_month)

    # Group records by employee ID
    employee_records = defaultdict(lambda: defaultdict(str))
    for record in records:
        employee_id, employee_name, docstatus, status, attendance_date, _ = record
        day = attendance_date.day

        if docstatus in [0, 2]:
            status = ""
        else:
            # Map status to desired abbreviations
            status_mapping = {"Present": "P", "Absent": "A",
                              "On Leave": "L", "Half Day": "HD", "Work From Home": "WFH"}
            status = status_mapping.get(status, "")

        employee_records[employee_id]['Employee Name'] = employee_name
        employee_records[employee_id][day] = status

    # Fill missing dates with empty strings
    for employee_attendance in employee_records.values():
        for day in range(1, last_day_of_month.day + 1):
            employee_attendance.setdefault(day, "")

    # Convert defaultdict to a list of dictionaries and sort dates
    formatted_data = []
    for employee_id, attendance_status in employee_records.items():
        sorted_dates = sorted(
            [day for day in attendance_status.keys() if day != 'Employee Name'], key=int)
        formatted_record = {
            "Employee": employee_id,
            "Employee Name": attendance_status['Employee Name'],
            **{day: attendance_status[day] for day in sorted_dates}
        }
        formatted_data.append(formatted_record)

    return columns, formatted_data, first_day_of_month, last_day_of_month


def fetch_attendance_records(company, employee, first_day_of_month, last_day_of_month):
    filters = {
        'attendance_date': ['between', [first_day_of_month, last_day_of_month]]
    }

    if employee != "None":
        filters['employee'] = employee

    if company != 'None':
        filters['company'] = company

    return frappe.get_all('Attendance',
                          filters=filters,
                          fields=['employee', 'employee_name', 'docstatus', 'status', 'attendance_date', 'company'],
                          order_by='attendance_date ASC')


@frappe.whitelist(allow_guest=True)
def get_employees():
    return frappe.get_all('Employee', filters={'status': 'Active'},
                          fields=['name', 'employee_name', 'company', 'status'])


@frappe.whitelist(allow_guest=True)
def get_company_list():
    return frappe.get_all('Company')
