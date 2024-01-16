
__version__ = '0.0.1'

from hrms.hr.doctype.interview.interview import Interview
from hrms.hr.doctype.attendance.attendance import Attendance
from hyde_app.api import set_average_rating
from hyde_app.api import mark_attendance_for_leave
Interview.set_average_rating = set_average_rating

Attendance.validate_attendance_date=mark_attendance_for_leave

from hrms.hr.doctype.job_applicant.job_applicant import JobApplicant
from hyde_app.role_perms_api import nameing_job_applicant_doctype 

JobApplicant.autoname = nameing_job_applicant_doctype