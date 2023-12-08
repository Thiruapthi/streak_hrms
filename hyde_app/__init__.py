
__version__ = '0.0.1'

from hrms.hr.doctype.interview.interview import Interview
from hyde_app.api import set_average_rating
Interview.set_average_rating = set_average_rating
