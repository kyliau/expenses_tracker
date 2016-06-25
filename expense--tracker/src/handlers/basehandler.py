import webapp2
from google.appengine.api import users
from src.models.appuser import AppUser

# Define a base handler that extends the dispatch() method to handle
# login
class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        user = users.get_current_user()
        # user must be defined because Google login is required
        assert user
        self.user = user
        appUser = AppUser.queryByUserId(user.user_id())
        if appUser:
            self.appUser = appUser
            webapp2.RequestHandler.dispatch(self)
        else:
            self.redirect("/register")