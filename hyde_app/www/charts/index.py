import frappe
from frappe import _
import datetime
from hrms.hr.report.monthly_attendance_sheet.monthly_attendance_sheet import execute

@frappe.whitelist(allow_guest= True)
def get_script_report_data(selectedMonthVal, filterByEmployeeVal, filterByYearVal, filterByCompany):

	if filterByEmployeeVal == 'None':
		filters = {
			"company":filterByCompany,
			"month":selectedMonthVal,
			"year":filterByYearVal,
			# "employee": filterByEmployeeVal
		}
		columns,data,message,chart = execute(filters)
		# print(data,"this is index.py data")
		return columns,data,message,chart
	else :
		filters = {
			"company":filterByCompany,
			"month":selectedMonthVal,
			"year":filterByYearVal,
			"employee": filterByEmployeeVal
		}
		columns,data,message,chart = execute(filters)
		# print(data,"this is index.py data")
		return columns,data,message,chart
	# print(data)
	# print(columns,data,"this is index.py data")

@frappe.whitelist(allow_guest=True)
def get_emplyees():
	employeeList = frappe.get_all('Employee', fields=['name', 'employee_name'])
	return employeeList

@frappe.whitelist(allow_guest=True)
def get_company_list():
	companyList = frappe.get_all('Company')
	return companyList