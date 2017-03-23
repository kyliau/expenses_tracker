from google.appengine.api import users
import webapp2
from src.models.appuser import AppUser
from src.utils.jinjautil import JINJA_ENVIRONMENT

class MainPage(webapp2.RequestHandler):
    """
    Show the landing page. No login is required for this page.
    If user has given permission for Expense Tracker to access their
    email address then this page would redirect user to the
    registration page. If user has already registered then user will
    be redirected to the user homepage.
    """
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
            template_location = "templates/landing.html"
            template = JINJA_ENVIRONMENT.get_template(template_location)
            self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    ("/", MainPage),
], debug=False)
