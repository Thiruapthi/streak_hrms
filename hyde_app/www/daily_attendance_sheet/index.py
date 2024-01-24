import frappe
from datetime import date
from collections import defaultdict

@frappe.whitelist(allow_guest=True)
def get_daily_attendance_report(start_date_str=None):
    try:
        # Parse provided start_date
        start_date = frappe.utils.getdate(start_date_str) if start_date_str else date.today()

        # Columns for the table
        columns = ["Employee", "On Leave", "Present", "Work From Home", "Half Day"]

        # Get all active employees
        employees = frappe.get_all('Employee', filters={'status': 'Active'}, fields=['name', 'employee_name'])

        # Fetch attendance records for the given date
        attendance_records = frappe.get_all('Attendance', filters={'attendance_date': start_date}, fields=['employee', 'status'])

        # Organize attendance records by employee
        employee_attendance = defaultdict(lambda: {
            "Employee": "",
            "On Leave": "",
            "Present": "",
            "Work From Home": "",
            "Half Day": ""
        })

        for record in attendance_records:
            employee_id, status = record['employee'], record['status']

            # Find the corresponding employee details
            employee_details = next((emp for emp in employees if emp['name'] == employee_id), None)

            if employee_details:
                employee_attendance[employee_id]['Employee'] = f"{employee_details['employee_name']}"
                if status == 'On Leave':
                    # If the employee is on leave, get the leave type
                    leave_type = get_leave_type(employee_id, start_date)
                    employee_attendance[employee_id][status] = f"{status} - {leave_type}" if leave_type else status
                else:
                    employee_attendance[employee_id][status] = status

        # Prepare the data for the table
        table_data = list(employee_attendance.values())
        frappe.log_error('table_data', table_data)

        return columns, table_data

    except Exception as e:
        frappe.log_error(f"Error in get_daily_attendance_report: {str(e)}")
        return None


def get_leave_type(employee_id, date):
    # Function to fetch the leave type for an employee on a given date
    leave_record = frappe.get_value('Attendance', {
        'employee': employee_id,
        'attendance_date': date,
    }, 'leave_type')
    return leave_record
