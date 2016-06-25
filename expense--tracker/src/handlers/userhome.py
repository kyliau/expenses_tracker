from google.appengine.api import users
from src.utils.jinjautil import JINJA_ENVIRONMENT
from src.handlers.basehandler import BaseHandler

class UserHomeHandler(BaseHandler):
    def get(self):
        appUser = self.appUser
        template_values = {
            "current_page" : "Home",
            "logout_url"   : users.create_logout_url("/"),
            "name"         : appUser.name,
            "projects"     : appUser.getAllProjects()
        }
        template = JINJA_ENVIRONMENT.get_template("templates/home.html")
        self.response.write(template.render(template_values))