
import datetime

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cstr, flt, get_datetime, get_link_to_form, getdate, nowtime
from hrms.hr.doctype.interview.interview import Interview as OriginalInterviewController

class CustomInterviewController(OriginalInterviewController):
    def after_insert(self):
        
        current_date = getdate()
        next_day = current_date + datetime.timedelta(days=1)
        
        job_Applicant_Email = self.job_applicant
        job_Applicant = self.custom_job_applicant_name
        designation = self.designation
        Schedule_On = self.scheduled_on
        from_time = self.from_time
        Interview_round = self.interview_round
        interview_type = self.custom_interview_type
        interview_link = self.custom_interview_link
        Schedule_On_date = getdate(Schedule_On)
        
        
        Interviewer_Name = self.interview_details[0].custom_interviewer_name
        Interviewer_Emails_List = self.interview_details
        interviewer_emails = []
        for each_interviewer in Interviewer_Emails_List:
            interviewer_emails.append(each_interviewer.interviewer)
        print(interviewer_emails)
        dynamic_link = self.resume_link
        if interview_type == "Offline":
            if Schedule_On_date <= next_day:
                Record_Name = self.name
                message = (
					_("Dear {0},").format(job_Applicant)
					+ "<br><br>"
					+ _("Greetings of the day!")
					+ "<br><br>"
					+ _("We are pleased to inform you that your Interview is scheduled for  {0} on {1} at {2}").format(designation,Schedule_On,from_time)
					+"<br><br>"
					+_("It will be a {0}").format(Interview_round)
					+"<br><br>"
					+_("Wishing you the best for your Interview.")
					+"<br><br>"
					+_("Thanks and regards,")
					+"<br><br>"
					+_("HR-Team KoreCent")
				)
                frappe.sendmail(
					recipients=job_Applicant_Email,
					subject="Interview Remainder",
					message=message,
					reference_doctype="Interview",
					reference_name=Record_Name,
				)
                Interviewer_message = (
					_("Dear {0},").format(Interviewer_Name)
					+"<br><br>"
					+_("Greetings of the day!")
					+"<br><br>"
					+_("An Interview has been scheduled for  {0} on {1} at {2}. Candidate name is {3}.").format(designation,Schedule_On,from_time,job_Applicant)
					+"<br><br>"
					+_("Below enclosed is the resume for your ")
					+f'<a href="{dynamic_link}"> Reference</a>'
					+"<br><br>"
					+_("Please ensure your availability for the Interview and incase of any rescheduling let us know 1 day in advance.")
					+"<br><br>"
					+_("Thanks and regards")
					+"<br><br>"
					+_("HR- Team KoreCent")
				)
                Interviewer_Subject = "Software Engineer interview " + Interview_round
                
                frappe.sendmail(
					recipients=interviewer_emails,
					subject=Interviewer_Subject,
					message=Interviewer_message,
					reference_doctype="Interview",
					reference_name=Record_Name,
				)
        else:
            if Schedule_On_date <= next_day:
                Record_Name = self.name
                message = (
					_("Dear {0},").format(job_Applicant)
					+ "<br><br>"
					+ _("Greetings of the day!")
					+ "<br><br>"
					+ _("We are pleased to inform you that your Interview is scheduled for  {0} on {1} at {2}").format(designation,Schedule_On,from_time)
					+"<br><br>"
					+_("It will be a {0}").format(Interview_round)
					+"<br><br>"
                    +_("Interview Link: {0}").format(interview_link)
                    +"<br><br>"
					+_("Wishing you the best for your Interview.")
					+"<br><br>"
					+_("Thanks and regards,")
					+"<br><br>"
					+_("HR-Team KoreCent")
				)
                frappe.sendmail(
					recipients=job_Applicant_Email,
					subject="Interview Remainder",
					message=message,
					reference_doctype="Interview",
					reference_name=Record_Name,
				)
                Interviewer_message = (
					_("Dear {0},").format(Interviewer_Name)
					+"<br><br>"
					+_("Greetings of the day!")
					+"<br><br>"
					+_("An Interview has been scheduled for  {0} on {1} at {2}. Candidate name is {3}.").format(designation,Schedule_On,from_time,job_Applicant)
					+"<br><br>"
					+_("Below enclosed is the resume for your ")
					+f'<a href="{dynamic_link}"> Reference</a>'
					+"<br><br>"
                    +_("Interview Link: {0}").format(interview_link)
                    +"<br><br>"
					+_("Please ensure your availability for the Interview and incase of any rescheduling let us know 1 day in advance.")
					+"<br><br>"
					+_("Thanks and regards")
					+"<br><br>"
					+_("HR- Team KoreCent")
				)
                Interviewer_Subject = "Software Engineer interview " + Interview_round
                
                frappe.sendmail(
					recipients=interviewer_emails,
					subject=Interviewer_Subject,
					message=Interviewer_message,
					reference_doctype="Interview",
					reference_name=Record_Name,
				)