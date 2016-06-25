import os
import urllib
import json
import jinja2
import webapp2
from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.ext import ndb
from datetime import datetime
from src.utils.jinjautil import JINJA_ENVIRONMENT

class Home(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        appUser = ettypes.AppUser.queryByUserId(user.user_id())
        if appUser:
            template_values = {
                'current_page' : "Home",
                'logout_url'   : users.create_logout_url('/'),
                'name'         : appUser.name,
                'projects'     : appUser.getAllProjects()
            }
            template = JINJA_ENVIRONMENT.get_template('templates/home.html')
            self.response.write(template.render(template_values))
        else:
            self.redirect('/register')

app = webapp2.WSGIApplication([
    ('/home', Home),
    ('/register', RegisterNewUser),
    ('/newproject', CreateNewProject),
    ('/project', ProjectHome),
    ('/summary', Summary),
    ('/admin', Admin),
    ('/settings', Settings),
    ('/request', RequestProcessor)
], debug=True)

