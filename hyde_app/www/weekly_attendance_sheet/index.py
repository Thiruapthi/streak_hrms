import frappe
import json
from datetime import date, timedelta
from collections import defaultdict

@frappe.whitelist(allow_guest=True)
def get_weekly_report(company,employee):
    current_date = date.today()
    start_date = current_date - timedelta(days=current_date.weekday())
    end_date = start_date + timedelta(days=4)

    columns = ["Employee", "Employee Name"]

    for day in range(5):
        current_day = start_date + timedelta(days=day)
        dateVal = current_day.strftime("%d %a").lstrip("0")
        columns.append(dateVal)
    
    records = []
    if employee=="":
        records.extend(list(frappe.db.sql(f"""SELECT employee,employee_name,docstatus,status,attendance_date,company FROM `tabAttendance` WHERE company='{company}' AND attendance_date BETWEEN '{start_date}' AND '{end_date}' ORDER BY attendance_date ASC """)))
    else:
        records.extend(list(frappe.db.sql(f"""SELECT employee,employee_name,docstatus,status,attendance_date,company FROM `tabAttendance` WHERE company='{company}' AND employee = '{employee}' AND attendance_date BETWEEN '{start_date}' AND '{end_date}' ORDER BY attendance_date ASC """)))

    # Group records by employee ID
    employee_records = defaultdict(lambda: defaultdict(str))
    for record in records:
        employee_id, employee_name,docstatus, status, attendance_date, _ = record
        day = attendance_date.day
        if docstatus==2:
            status = ""
            employee_records[employee_id]['Employee Name'] = employee_name
            employee_records[employee_id][day] = status
        elif docstatus ==0:
            status = ""    
            employee_records[employee_id]['Employee Name'] = employee_name
            employee_records[employee_id][day] = status

        else:
            if status == "Present":
                status = "P"
            elif status == "Absent":
                status = "A"
            elif status == "On Leave":
                status = "L"
            elif status == "Half Day":
                status = "HD"
            elif status == "Work From Home":
                status = "WFH"

            employee_records[employee_id]['Employee Name'] = employee_name
            employee_records[employee_id][day] = status
             
    # Fill missing dates with empty strings
    for employee_attendance in employee_records.values():
        for day in range((start_date - end_date).days + 1):
            date_to_check = start_date + timedelta(days=day)
            day = date_to_check.day
            if day not in employee_attendance:
                employee_attendance[day] = ""

    # Convert defaultdict to a list of dictionaries and sort dates
    formatted_data = []
    for employee_id, attendance_status in employee_records.items():
        sorted_dates = sorted([day for day in attendance_status.keys() if day != 'Employee Name'], key=int)
        formatted_record = {
            "Employee": employee_id,
            "Employee Name": attendance_status['Employee Name'],
            **{day: attendance_status[day] for day in sorted_dates}
        }
        formatted_data.append(formatted_record)

    return  columns,formatted_data, end_date, start_date

@frappe.whitelist(allow_guest=True)
def get_employees():
	employeeList = frappe.get_all('Employee',filters={'status':'Active'},fields=['name', 'employee_name','company','status'])
	return employeeList

@frappe.whitelist(allow_guest=True)
def get_company_list():
	companyList = frappe.get_all('Company')
	return companyList