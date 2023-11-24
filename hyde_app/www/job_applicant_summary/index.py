import frappe

@frappe.whitelist()
def get_job_applicant_summary(positions):
    result = {}

    # Fetch job openings
    positions = frappe.get_all("Job Opening", fields=["name"], filters={"name": positions})
    result["positions"] = positions

    # Get round names for the specified job opening
    round_names = get_round_names(positions[0]["name"]) if positions else []

    # Fetch job applicants and their round statuses
    applicants = frappe.get_list("Job Applicant", filters={"job_title": positions[0]["name"]}, fields=["name", "applicant_name", "status"])
    for applicant in applicants:
        rounds_cleared = get_rounds_cleared(applicant["name"])
        applicant["rounds_cleared"] = rounds_cleared
        
    if applicants and round_names: 
        # Store the results in the dictionary
        result["positions"] = positions
        result["rounds"] = {
            "applicants": applicants,
            "round_names": round_names
        }
    else:
        result["data"]="no data found"
    return result

def get_round_names(job_opening_name):
    # Fetch round names from custom_round field in Job Opening
    job_opening = frappe.get_doc("Job Opening", job_opening_name)
    return [round.interview_rounds for round in job_opening.custom_round]

def get_rounds_cleared(job_applicant):
    # Fetch the status of the interview for the specified job applicant
    interview = frappe.get_all("Interview", filters={"job_applicant": job_applicant}, fields=["status"])
    
    if interview:
        return interview[0].status
    return None 

@frappe.whitelist()
def get_job_openings():
    # Fetch all open job openings to show in filters
    positions = frappe.get_all("Job Opening", fields=["name"], filters={"status": "Open"})
    return positions
