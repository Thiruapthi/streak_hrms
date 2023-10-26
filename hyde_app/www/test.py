import frappe
import subprocess
import json
import erpnext



def update_opportunity_sales_stage_1():
    lists = frappe.get_all("Sales Stage",as_list=True)
    flattened_list = [item for sublist in lists for item in sublist]
    return flattened_list
   

def migrate():
    command = ["bench", "migrate"]

    # Run the command
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        print("Command output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Command failed with error:", e)
        print("Error output:", e.stderr)



@frappe.whitelist(allow_guest=True) 
def write_options(doc={},method=""):
    ind = 0
    file_path = '/home/yash/New-Hr/apps/hyde_app/hyde_app/hyde/custom/opportunity.json'
    new_options = update_opportunity_sales_stage_1()
    if doc:
        print(True,"\n\n\n\n")
        item_index = new_options.index(doc.name)
        if item_index != -1:
            new_options.pop(item_index)
    new_options ="\n".join(new_options)
    # Load the JSON content from the file
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    
    for i in range(len(data["custom_fields"])):
        if data["custom_fields"][i]["fieldname"] == "custom_test":
          ind = i
          break

    data['custom_fields'][ind]['options'] = new_options
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file,indent=1)
    
    migrate()

# import frappe
# import subprocess
# import json

# def update_opportunity_sales_stage_1():
#     sales_stages = frappe.get_all("Sales Stage", as_list=True)
#     flattened_list = [item for sublist in sales_stages for item in sublist]
#     return flattened_list

# def migrate():
#     command = ["bench", "migrate"]

#     try:
#         result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
#         print("Command output:", result.stdout)
#     except subprocess.CalledProcessError as e:
#         print("Command failed with error:", e)
#         print("Error output:", e.stderr)

# @frappe.whitelist(allow_guest=True)
# def write_options(doc="", method=""):
#     ind = 0
#     file_path = '/home/yash/Demohr/apps/hyde_app/hyde_app/hyde/custom/opportunity.json'
#     new_options = update_opportunity_sales_stage_1()
    
#     if doc in new_options:
#         new_options.remove(doc)
    
#     new_options = "\n".join(new_options)
    
#     with open(file_path, 'r') as json_file:
#         data = json.load(json_file)
    
#     for i in range(len(data["custom_fields"])):
#         if data["custom_fields"][i]["fieldname"] == "custom_test":
#             ind = i
#             break

#     data['custom_fields'][ind]['options'] = new_options
#     with open(file_path, 'w') as json_file:
#         json.dump(data, json_file, indent=1)
    
#     migrate()

