import frappe
from datetime import date, timedelta
from collections import defaultdict


@frappe.whitelist(allow_guest=True)
def get_weekly_report(company, employee, start_date_str=None, end_date_str=None):
    frappe.log_error("start_date_str",start_date_str)
    frappe.log_error("end_date_str",end_date_str)
    start_date, end_date = calculate_date_range(start_date_str, end_date_str)
    

    columns = ["Employee", "Employee Name"] + [current_day.strftime(
        "%d %a").lstrip("0") for current_day in date_range(start_date, end_date)]

    records = fetch_attendance_records(company, employee, start_date, end_date)

    # Group records by employee ID
    employee_records = group_records_by_employee(records)

    # Fill missing dates with empty strings
    fill_missing_dates(employee_records, start_date, end_date)

    # Convert defaultdict to a list of dictionaries and sort dates
    formatted_data = format_attendance_data(employee_records)

    return columns, formatted_data, end_date, start_date


def calculate_date_range(start_date_str, end_date_str):
    if not start_date_str or not end_date_str:
        # If start_date or end_date is not provided, use the current week
        current_date = date.today()
        start_date = current_date - timedelta(days=current_date.weekday())
        end_date = start_date + timedelta(days=4)
    else:
        # Parse provided start_date and end_date
        start_date = frappe.utils.getdate(start_date_str)
        end_date = frappe.utils.getdate(end_date_str)
    return start_date, end_date


def date_range(start_date, end_date):
    return [start_date + timedelta(days=day) for day in range((end_date - start_date).days + 1)]


def fetch_attendance_records(company, employee, start_date, end_date):
    sql_query = f"""SELECT employee, employee_name, docstatus, status, attendance_date, company
                   FROM `tabAttendance`
                   WHERE company='{company}' AND attendance_date BETWEEN '{start_date}' AND '{end_date}'"""
    if employee:
        sql_query += f" AND employee = '{employee}'"
    
    sql_query += " ORDER BY attendance_date ASC"

    return frappe.db.sql(sql_query)



def group_records_by_employee(records):
    employee_records = defaultdict(lambda: defaultdict(str))
    for record in records:
        employee_id, employee_name, docstatus, status, attendance_date, _ = record
        day = attendance_date.day
        status = "" if docstatus in [0, 2] else get_status_abbreviation(status)

        employee_records[employee_id]['Employee Name'] = employee_name
        employee_records[employee_id][day] = status

    return employee_records


def fill_missing_dates(employee_records, start_date, end_date):
    for employee_attendance in employee_records.values():
        for day in date_range(start_date, end_date):
            if day.day not in employee_attendance:
                employee_attendance[day.day] = ""


def format_attendance_data(employee_records):
    formatted_data = []
    for employee_id, attendance_status in employee_records.items():
        sorted_dates = sorted(
            [day for day in attendance_status.keys() if day != 'Employee Name'], key=int)
        formatted_record = {
            "Employee": employee_id,
            "Employee Name": attendance_status['Employee Name'],
            **{str(day): attendance_status[day] for day in sorted_dates}
        }
        formatted_data.append(formatted_record)

    return formatted_data


def get_status_abbreviation(status):
    status_mapping = {"Present": "P", "Absent": "A",
                      "On Leave": "L", "Half Day": "HD", "Work From Home": "WFH"}
    return status_mapping.get(status, "")


@frappe.whitelist(allow_guest=True)
def get_employees():
    return frappe.get_all('Employee', filters={'status': 'Active'}, fields=['name', 'employee_name', 'company', 'status'])


@frappe.whitelist(allow_guest=True)
def get_company_list():
    return frappe.get_all('Company')
