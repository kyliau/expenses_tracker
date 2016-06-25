#import webapp2
from src.utils.jinjautil import JINJA_ENVIRONMENT
#from src.models.appuser import AppUser
from src.handlers.basehandler import BaseHandler

class UserHomeHandler(BaseHandler):
    def get(self):
        appUser = None
        print "USER = ", self.user
        print "APPUSER = ", self.appUser
        #user = users.get_current_user()
        #appUser = AppUser.queryByUserId(user.user_id())
        if appUser:
            template_values = {
                'current_page' : "Home",
                #'logout_url'   : users.create_logout_url('/'),
                'name'         : appUser.name,
                'projects'     : appUser.getAllProjects()
            }
            template = JINJA_ENVIRONMENT.get_template('templates/home.html')
            self.response.write(template.render(template_values))
        else:
            self.redirect('/register')