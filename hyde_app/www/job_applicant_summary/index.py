import frappe

@frappe.whitelist()
def get_job_applicant_summary(positions):
    applicants = frappe.get_list("Job Applicant", filters={"job_title": positions}, fields=["name", "applicant_name", "status"])
    interview_details = {"applicants": [], "round_names": get_round_names(positions) if positions else []}

    for applicant in applicants:
        rounds_cleared = get_rounds_cleared(applicant["name"])
        applicant["rounds_cleared"] = rounds_cleared
        interview_details["applicants"].append(applicant)

    result = {"interview_details": interview_details, "data": "No data found" if not applicants else None}
    return result

def get_round_names(job_opening_name):
    job_opening = frappe.get_doc("Job Opening", job_opening_name)
    return [round.interview_rounds for round in job_opening.custom_round]

def get_rounds_cleared(job_applicant):
    interview = frappe.get_all("Interview", filters={"job_applicant": job_applicant}, fields=["status", "interview_round"])

    return interview if interview else None

@frappe.whitelist()
def get_job_openings():
    positions = frappe.get_all("Job Opening", fields=["name"], filters={"status": "Open"})
    return positions
