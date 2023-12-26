from . import __version__ as app_version

app_name = "hyde_app"
app_title = "Hyde"
app_publisher = "hyde"
app_description = "abc"
app_email = "hyde.k@korecent.com"
app_license = "MIT"

# Includes in <head>
# ------------------
# fixtures = [{"doctype": "Notification", "filters": {"name": ["in", ["Job Applicant Email","interviewer - Recruitment"]]}}]
# include js, css files in header of desk.html
# app_include_css = "/assets/hyde_app/css/hyde_app.css"
# app_include_js = "/assets/hyde_app/js/hyde_app.js"
app_include_js = "/assets/hyde_app/js/attach.js"

# include js, css files in header of web template
# web_include_css = "/assets/hyde_app/css/hyde_app.css"
# web_include_js = "/assets/hyde_app/js/hyde_app.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "hyde_app/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"Role": "public/js/role.js",
              "Opportunity": "public/js/opportunity.js",
              "Sales Stage": "public/js/sales_stage.js",
              "Leave Application": "public/js/leave_application.js",
              "Job Applicant": "public/js/job_applicant.js",
              "Appointment Letter": "public/js/ap_letter.js",
              "Employee": "public/js/employee.js",
              "Interview": "public/js/interview.js",
              "Job Offer": "public/js/job_offer.js",
              "Employee Onboarding": "public/js/employee_onboarding.js",
              "Compensatory Leave Request": "public/js/compensatory_leave_request.js",
              "Interview Feedback": "public/js/interview_feedback.js"
              }
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# "Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# "methods": "hyde_app.utils.jinja_methods",
# "filters": "hyde_app.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "hyde_app.install.before_install"
# after_install = "hyde_app.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "hyde_app.uninstall.before_uninstall"
# after_uninstall = "hyde_app.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "hyde_app.utils.before_app_install"
# after_app_install = "hyde_app.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "hyde_app.utils.before_app_uninstall"
# after_app_uninstall = "hyde_app.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "hyde_app.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# "Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# "Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
    # "ToDo": "custom_app.overrides.CustomToDo"
    "Interview": "hyde_app.Controllers.interview.CustomInterviewController"
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    # "*": {
    # "on_update": "method",
    # "on_cancel": "method",
    # "on_trash": "method"
    # }
    "Sales Stage": {
        "after_delete": "hyde_app.www.Kanban_Sales.update_custom_select_field"
    },
    "Interview": {
        "on_update": "hyde_app.api.notify_hr_on_interview_update",
        "after_insert": "hyde_app.api.send_email_on_interview_scheduled"
    },
    "Appointment Letter": {
        "after_insert": "hyde_app.api.send_appointment_email",
    },
    "Compensatory Leave Request": {
        "on_update": "hyde_app.api.send_compensatory_leave_request"
    },
    "Job Offer": {
        "after_insert": "hyde_app.api.send_Job_offer_email",
    },
    "Job Applicant": {
        "after_insert": "hyde_app.api.send_job_applicant_creation_email",
        "on_update": "hyde_app.api.send_rejection_email_to_job_applicant_if_not_sent"
    },
    "Leave Application": {
        "after_insert": "hyde_app.api.mark_attendance_for_applied_leave"
    }
}
# Scheduled Tasks
# ---------------

# scheduler_events = {
# "all": [
# "hyde_app.tasks.all"
# ],
# "daily": [
# "hyde_app.tasks.daily"
# ],
# "hourly": [
# "hyde_app.tasks.hourly"
# ],
# "weekly": [
# "hyde_app.tasks.weekly"
# ],
# "monthly": [
# "hyde_app.tasks.monthly"
# ],
# }
scheduler_events = {
    "daily": [
        "hyde_app.api.execute_job_offer_workflow"
    ]
}
# Testing
# -------

# before_tests = "hyde_app.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
    "frappe.desk.calendar.get_events": "hyde_app.api.get_events"
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# "Task": "hyde_app.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["hyde_app.utils.before_request"]
# after_request = ["hyde_app.utils.after_request"]

# Job Events
# ----------
# before_job = ["hyde_app.utils.before_job"]
# after_job = ["hyde_app.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# {
# "doctype": "{doctype_1}",
# "filter_by": "{filter_by}",
# "redact_fields": ["{field_1}", "{field_2}"],
# "partial": 1,
# },
# {
# "doctype": "{doctype_2}",
# "filter_by": "{filter_by}",
# "partial": 1,
# },
# {
# "doctype": "{doctype_3}",
# "strict": False,
# },
# {
# "doctype": "{doctype_4}"
# }
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# "hyde_app.auth.validate"
# ]
