from google.appengine.api import users
import os
import jinja2
import webapp2
import ettypes

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            appUser = ettypes.AppUser.queryByUserId(user.user_id())
            if appUser:
                self.redirect('/home')
            else:
                self.redirect('/register')
        else:
            url = users.create_login_url(self.request.uri)
            template_values = { 'url': url }
            template = JINJA_ENVIRONMENT.get_template('templates/index.html')
            self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)

