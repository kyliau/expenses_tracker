from google.appengine.api import users
from src.handlers.basehandler import BaseHandler
from src.utils.jinjautil import JINJA_ENVIRONMENT

class SettingsHandler(BaseHandler):
    def get(self):
        #user = users.get_current_user()
        #appUser = ettypes.AppUser.queryByUserId(user.user_id())
        #if not appUser:
        #    self.abort(401)
        appUser = self.appUser
        template = JINJA_ENVIRONMENT.get_template("templates/settings.html")
        template_values = {
            "current_page" : "Settings",
            "logout_url"   : users.create_logout_url('/'),
            "projects"     : appUser.getAllProjects(),
            "settings"     : appUser.settings,
            "app_user"     : appUser
        }
        self.response.write(template.render(template_values))

    def post(self):
        #user = users.get_current_user()
        #appUser = ettypes.AppUser.queryByUserId(user.user_id())
        #if not appUser:
        #    self.abort(401)
        appUser = self.appUser
        settingsChanged = False
        for index, project in enumerate(appUser.projects):
            existingEmailOption = appUser.settings[index]
            emailOption = self.request.get(project.urlsafe() + "_email")
            if emailOption in ["all", "relevant", "none"] and emailOption != existingEmailOption.receive_email:
                existingEmailOption.receive_email = emailOption
                settingsChanged = True
        if settingsChanged:
            appUser.put()
        self.response.write("Success! Your settings have been updated.")