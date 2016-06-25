import webapp2
#from google.appengine.api import users
#from google.appengine.ext import ndb

from src.handlers.register import RegisterHandler
from src.handlers.userhome import UserHomeHandler
from src.handlers.newproject import NewProjectHandler
from src.handlers.projecthome import ProjectHomeHandler
from src.handlers.summary import SummaryHandler
from src.handlers.admin import AdminHandler
from src.handlers.settings import SettingsHandler
from src.handlers.ajax import AjaxHandler

app = webapp2.WSGIApplication([
    ("/home", UserHomeHandler),
    ("/register", RegisterHandler),
    ("/newproject", NewProjectHandler),
    ("/project", ProjectHomeHandler),
    ("/summary", SummaryHandler),
    ("/admin", AdminHandler),
    ("/settings", SettingsHandler),
    ("/request", AjaxHandler)
], debug=True)

