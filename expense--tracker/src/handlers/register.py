import webapp2
from google.appengine.api import users
from src.models.appuser import AppUser
from src.utils.jinjautil import JINJA_ENVIRONMENT

class RegisterHandler(webapp2.RequestHandler):
    def get(self):
        # need to check if user is actually registered
        user = users.get_current_user()
        assert user
        template = JINJA_ENVIRONMENT.get_template('templates/register.html')
        self.response.write(template.render())
        # potential improvement: 
        # add a query to signify where to redirect after user registers an
        # account

    def post(self):
        user = users.get_current_user()
        assert user
        #assert user is not None
        name = self.request.get('name', '')
        assert name
        newUser = AppUser.addRegisteredUser(user=user, name=name)
        assert newUser
        self.redirect('/home')