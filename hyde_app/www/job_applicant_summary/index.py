import frappe

@frappe.whitelist()
def get_job_applicant_summary(positions):
    result = {}

    # Fetch job applicants and their round statuses
    applicants = frappe.get_list("Job Applicant", filters={"job_title": positions}, fields=["name", "applicant_name", "status"])
    for applicant in applicants:
        rounds_cleared = get_rounds_cleared(applicant["name"])
        applicant["rounds_cleared"] = rounds_cleared
        
    if applicants: 
        result["interview_details"] = {
            "applicants": applicants,
            "round_names": get_round_names(positions) if positions else []
        }
    else:
        result["data"]="No data found"
    return result

def get_round_names(job_opening_name):
    # Fetch round names from custom_round field in Job Opening
    job_opening = frappe.get_doc("Job Opening", job_opening_name)
    return [round.interview_rounds for round in job_opening.custom_round]

def get_rounds_cleared(job_applicant):
    # Fetch the status of the interview for the specified job applicant
    interview = frappe.get_all("Interview", filters={"job_applicant": job_applicant}, fields=["status","interview_round"])

    if interview:
        return interview
    return None 

@frappe.whitelist()
def get_job_openings():
    # Fetch all open job openings to show in filters
    positions = frappe.get_all("Job Opening", fields=["name"], filters={"status": "Open"})
    return positions
