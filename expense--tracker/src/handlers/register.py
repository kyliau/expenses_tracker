import webapp2
from google.appengine.api import users
from src.models.appuser import AppUser
from src.utils.jinjautil import JINJA_ENVIRONMENT

class RegisterHandler(webapp2.RequestHandler):
    def get(self):
        """
        Return the registration page if the current user has not
        registered. Otherwise redirect the user to user homepage.
        """
        user = users.get_current_user()
        # user must be defined because Google login is required
        assert user
        # need to check if user is actually registered
        appUser = AppUser.queryByUserId(user.user_id())
        if appUser is None or appUser.isNew():
            template = JINJA_ENVIRONMENT.get_template('templates/register.html')
            self.response.write(template.render())
        else:
            self.redirect("/home")

    def post(self):
        """
        Register a new user with name and user_id.
        """
        user = users.get_current_user()
        # user must be defined because Google login is required
        assert user
        appUser = AppUser.create(user.email())
        if appUser.isNew():
            appUser.name = self.request.get("name")
            appUser.user_id = user.user_id()
            appUser.put()
        self.redirect("/home")