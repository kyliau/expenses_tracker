#import os
#import urllib
#import json
#import jinja2
import webapp2
#from google.appengine.api import mail
#from google.appengine.api import users
#from google.appengine.ext import ndb
#from datetime import datetime
#from src.utils.jinjautil import JINJA_ENVIRONMENT

from src.handlers.register import RegisterHandler
from src.handlers.userhome import UserHomeHandler
from src.handlers.newproject import NewProjectHandler

app = webapp2.WSGIApplication([
    ('/home', UserHomeHandler),
    ('/register', RegisterHandler),
    ('/newproject', NewProjectHandler),
    #('/project', ProjectHome),
    #('/summary', Summary),
    #('/admin', Admin),
    #('/settings', Settings),
    #('/request', RequestProcessor)
], debug=True)

