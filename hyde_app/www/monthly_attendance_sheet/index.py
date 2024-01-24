import frappe
from frappe import _
import datetime
from datetime import date, timedelta
from collections import defaultdict
from hrms.hr.report.monthly_attendance_sheet.monthly_attendance_sheet import execute


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

    records = []

    if employee == "None" and company == 'None':
        records.extend(list(frappe.db.sql(f"""SELECT att.employee, att.employee_name, att.docstatus, att.status, 
                                             att.attendance_date, att.company, `leave`.leave_type
                                          FROM `tabAttendance` att
                                          LEFT JOIN `tabLeave Application` `leave` 
                                          ON att.employee = `leave`.employee
                                          AND att.attendance_date BETWEEN `leave`.from_date AND `leave`.to_date
                                          WHERE att.attendance_date BETWEEN '{first_day_of_month}' AND '{last_day_of_month}' 
                                          ORDER BY att.attendance_date ASC""")))

    elif employee == "None":
        records.extend(list(frappe.db.sql(f"""SELECT att.employee, att.employee_name, att.docstatus, att.status, 
                                             att.attendance_date, att.company, `leave`.leave_type
                                          FROM `tabAttendance` att
                                          LEFT JOIN `tabLeave Application` `leave` 
                                          ON att.employee = `leave`.employee
                                          AND att.attendance_date BETWEEN `leave`.from_date AND `leave`.to_date
                                          WHERE att.attendance_date BETWEEN '{first_day_of_month}' AND '{last_day_of_month}' 
                                          ORDER BY att.attendance_date ASC""")))
    else:
        records.extend(list(frappe.db.sql(f"""SELECT att.employee, att.employee_name, att.docstatus, att.status, 
                                                 att.attendance_date, att.company, leave.leave_type
                                              FROM `tabAttendance` att
                                              LEFT JOIN `tabLeave Application` `leave` 
                                              ON att.employee = leave.employee
                                              AND att.attendance_date BETWEEN leave.from_date AND leave.to_date
                                              WHERE att.company='{company}' 
                                              AND att.employee = '{employee}' 
                                              AND att.attendance_date BETWEEN '{first_day_of_month}' AND '{last_day_of_month}' 
                                              ORDER BY att.attendance_date ASC""")))

    # Group records by employee ID
    employee_records = defaultdict(lambda: defaultdict(str))
    for record in records:
        employee_id, employee_name, docstatus, status, attendance_date, _, leave_type = record
        day = attendance_date.day

        if docstatus == 2:
            status = ""
            leave_type = ""
            employee_records[employee_id]['Employee Name'] = employee_name
            employee_records[employee_id]['Leave Type'] = leave_type
            employee_records[employee_id][day] = status
        elif docstatus == 0:
            status = ""
            leave_type = ""
            employee_records[employee_id]['Employee Name'] = employee_name
            employee_records[employee_id]['Leave Type'] = leave_type
            employee_records[employee_id][day] = status
        else:
            if status == "On Leave":
                # Fetch the leave type when status is "On Leave"
                status = leave_type  # Set status to leave type for "On Leave" entries
            else:
                # Map status to desired abbreviations for other cases
                status_mapping = {"Present": "P", "Absent": "A",
                                  "Half Day": "HD", "Work From Home": "WFH"}
                status = status_mapping.get(status, "")

            employee_records[employee_id]['Employee Name'] = employee_name
            employee_records[employee_id][day] = status

    # Fill missing dates with empty strings
    for employee_attendance in employee_records.values():
        for day in range(1, last_day_of_month.day + 1):
            if day not in employee_attendance:
                employee_attendance[day] = ""

    # Convert defaultdict to a list of dictionaries and sort dates
    formatted_data = []
    for employee_id, attendance_status in employee_records.items():
        sorted_dates = sorted([day for day in attendance_status.keys() if day not in [
                              'Employee Name', 'Leave Type']], key=int)
        formatted_record = {
            "Employee": employee_id,
            "Employee Name": attendance_status['Employee Name'],
            **{day: attendance_status[day] for day in sorted_dates}
        }
        formatted_data.append(formatted_record)

    return columns, formatted_data, first_day_of_month, last_day_of_month


@frappe.whitelist(allow_guest=True)
def get_employees():
    employeeList = frappe.get_all('Employee', filters={'status': 'Active'}, fields=[
                                  'name', 'employee_name', 'company', 'status'])
    return employeeList


@frappe.whitelist(allow_guest=True)
def get_company_list():
    companyList = frappe.get_all('Company')
    return companyList