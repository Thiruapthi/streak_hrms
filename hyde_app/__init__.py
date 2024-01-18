
__version__ = '0.0.1'

from hrms.hr.doctype.interview.interview import Interview
from hrms.hr.doctype.attendance.attendance import Attendance
from hyde_app.api import set_average_rating,mark_attendance_for_leave,reschedule_interview

Interview.set_average_rating = set_average_rating
Interview.reschedule_interview=reschedule_interview

Attendance.validate_attendance_date=mark_attendance_for_leave