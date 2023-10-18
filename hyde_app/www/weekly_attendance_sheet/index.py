import frappe
from datetime import date,timedelta
from hrms.hr.report.monthly_attendance_sheet.monthly_attendance_sheet import execute

@frappe.whitelist(allow_guest=True)
def get_weekly_report(company,employee):

    current_date = date.today()
    current_month = int((current_date.strftime("%Y-%m-%d")).split("-")[1])
    current_year = int((current_date.strftime("%Y-%m-%d")).split("-")[0])

    frappe.log_error("curent_date",current_date)
    frappe.log_error("current_month",current_month)
    frappe.log_error("current_year",current_year)
    frappe.log_error("company",company)
    frappe.log_error("employee",employee)



    filters ={
            'month': current_month, 'year':current_year, 'company': company,'employee': employee

		}
    columns, data, message, chart = execute(filters)

    frappe.log_error("columns",data)
    frappe.log_error("columns",columns)

    updatedcolumns = []
    updateddata = []

    current_date_num = int((current_date.strftime("%Y-%m-%d")).split("-")[2])

    previous_start_date = current_date+timedelta(days=-6)
    previous_start_date_num = int((previous_start_date.strftime("%Y-%m-%d")).split("-")[2])

    frappe.log_error("current_date_num",current_date_num)
    frappe.log_error("previous_start_date", previous_start_date)
    frappe.log_error("previous_start_date_num",previous_start_date_num)



    for eachcolumn in columns:
        if (type(eachcolumn["fieldname"])==int):
            if previous_start_date_num<=eachcolumn["fieldname"]<=current_date_num:
                updatedcolumns.append(eachcolumn)

        elif (type(eachcolumn["fieldname"])==str):
            updatedcolumns.append(eachcolumn)


    for eachrow in data:
        eachrowobj = {}
        for i in eachrow:
            if type(i)==int:
                if previous_start_date_num<=i<=current_date_num:
                    eachrowobj[i] = eachrow[i]

            elif (type(i)==str):
                eachrowobj[i] = eachrow[i]
        updateddata.append(eachrowobj)   

        
    

    present_date = date.today()
    previous_date = present_date+timedelta(days=-6)
    present_date = present_date.strftime("%d-%m-%Y")
    previous_date = previous_date.strftime("%d-%m-%Y")

    
    frappe.log_error("updatedColumns",updatedcolumns)
    frappe.log_error("updatedData",updateddata)
    frappe.log_error("present_date", present_date)
    frappe.log_error("previous_date",previous_date)

    return updatedcolumns,updateddata,present_date,previous_date

    
@frappe.whitelist(allow_guest=True)
def get_employee_id(inputName):

    frappe.log_error("inputName")
    employees_data = frappe.get_all("Employee", fields = '*')
    for each_employee_data in employees_data:
        if(inputName.lower()==each_employee_data.first_name.lower()):
            frappe.log_error("each_employee_Id",each_employee_data.name)
            return (each_employee_data.name)
