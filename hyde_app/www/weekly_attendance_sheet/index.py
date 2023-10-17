import frappe
from datetime import date,timedelta
from hrms.hr.report.monthly_attendance_sheet.monthly_attendance_sheet import execute

@frappe.whitelist(allow_guest=True)
def get_weekly_report(company,employee):

    current_date = date.today()
    current_month = int((current_date.strftime("%Y-%m-%d")).split("-")[1])
    current_year = int((current_date.strftime("%Y-%m-%d")).split("-")[0])

    filters ={
            'month': current_month, 'year':current_year, 'company': company,'employee': employee

		}
    columns, data, message, chart = execute(filters)

    updatedcolumns = []
    updateddata = []

    current_date_num = int((current_date.strftime("%Y-%m-%d")).split("-")[2])

    previous_start_date = current_date+timedelta(days=-6)
    previous_start_date_num = int((previous_start_date.strftime("%Y-%m-%d")).split("-")[2])

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

    return updatedcolumns,updateddata,present_date,previous_date

    
@frappe.whitelist(allow_guest=True)
def get_employee_id(inputName):
    employees_data = frappe.get_all("Employee", fields = '*')
    for each_employee_data in employees_data:
        if(inputName.lower()==each_employee_data.first_name.lower()):
            return (each_employee_data.name)
