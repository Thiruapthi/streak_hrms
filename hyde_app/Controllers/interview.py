
import datetime

import frappe
from frappe import _

from frappe import _
from frappe.model.document import Document
from frappe.utils import cstr, flt, get_datetime, get_link_to_form, getdate, nowtime, get_time
from hrms.hr.doctype.interview.interview import Interview as OriginalInterviewController
from google.oauth2 import service_account
from googleapiclient.discovery import build
SCOPES = "https://www.googleapis.com/auth/calendar"
from frappe.integrations.google_oauth import GoogleOAuth
import google.oauth2.credentials

class CustomInterviewController(OriginalInterviewController):
    def after_insert(self):
        
        current_date = getdate()
        # next_day = current_date + datetime.timedelta(days=1)
        
        job_Applicant_Email = self.job_applicant
        # job_Applicant = self.custom_job_applicant_name
        designation = self.designation
        Schedule_On = self.scheduled_on
        from_time = self.from_time
        end_time = self.to_time
        # Interview_round = self.interview_round
        # interview_type = self.custom_interview_type
        # interview_link = self.custom_interview_link
        Interviewer_Email = self.interview_details[0].interviewer
        Schedule_On_date = getdate(Schedule_On)
        
        
        # Interviewer_Name = self.interview_details[0].custom_interviewer_name
        Interviewer_Emails_List = self.interview_details
        interviewer_emails = []
        
        for each_interviewer in Interviewer_Emails_List:
            interviewer_emails.append(each_interviewer.interviewer)
            
        # dynamic_link = self.resume_link
        from_time_F = get_time(from_time)
        Combine_Date_F = datetime.datetime.combine(Schedule_On_date,from_time_F)
        end_time_E = get_time(end_time)
        Combine_Date_E = datetime.datetime.combine(Schedule_On_date,end_time_E)
        time_difference = datetime.timedelta(hours=6, minutes=30)
        new_from_date = Combine_Date_F + time_difference
        new_end_date =  Combine_Date_E + time_difference
        
        if new_from_date.hour >= 12:
            new_from_date -= datetime.timedelta(hours=12)
            new_end_date  -= datetime.timedelta(hours=12)
        N_date_F = new_from_date.date()
        N_time_F = new_from_date.time()
        N_date_E = new_end_date.date()
        N_time_E = new_end_date.time()
        Final_F_date = str(N_date_F)+"T"+str(N_time_F)+"Z"
        Final_E_date = str(N_date_E)+"T"+str(N_time_E)+"Z"
        try:
            google_settings = frappe.get_single("Google Settings")
            user_email = frappe.get_value("User", frappe.session.user, "email")
            Google_Account = frappe.db.get_list('Google Calendar',filters={'user':user_email},pluck="name")
            account = frappe.get_doc("Google Calendar", Google_Account[0])
            credentials_dict = {
			"token": account.get_access_token(),
			"refresh_token": account.get_password(fieldname="refresh_token", raise_exception=False),
			"token_uri": GoogleOAuth.OAUTH_URL,
			"client_id": google_settings.client_id,
			"client_secret": google_settings.get_password(fieldname="client_secret", raise_exception=False),
			"scopes": ["https://www.googleapis.com/auth/calendar/v3"],
			}
            
            credentials = google.oauth2.credentials.Credentials(**credentials_dict)
            service = build('calendar', 'v3', credentials=credentials)
            event = {
				'summary': 'Interview Schedule',
				'description': 'Interview for '+designation,
				'start': {
					'dateTime': Final_F_date,  # Use RFC3339 date-time format
					'timeZone': 'Asia/Kolkata',
				},
				'end': {
					'dateTime': Final_E_date,
					'timeZone': 'Asia/Kolkata',
				},
				'attendees': [
					{'email': job_Applicant_Email},
					{'email': Interviewer_Email},
					# Add more attendees as needed
				],
				'sendNotifications': True,
				'reminders': {
					'useDefault': False,  # Disable default reminders
					'overrides': [
						{'method': 'popup', 'minutes': 10},  # Set a 30-minute popup reminder
						{'method': 'email', 'minutes': 60},  # Set a 1-hour email reminder
					]
				},
				
			}
            
            created_event = service.events().insert(calendarId='primary', body=event).execute()
            
        except IndexError:
             pass