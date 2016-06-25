from google.appengine.api import users
import webapp2
from src.models.appuser import AppUser
from src.utils.jinjautil import JINJA_ENVIRONMENT

class MainPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            appUser = AppUser.queryByUserId(user.user_id())
            if appUser:
                self.redirect("/home")
            else:
                self.redirect("/register")
        else:
            url = users.create_login_url(self.request.uri)
            template_values = { "url" : url }
            template = JINJA_ENVIRONMENT.get_template("templates/index.html")
            self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    ("/", MainPage),
], debug=True)