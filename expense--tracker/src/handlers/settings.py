from google.appengine.api import users
from src.handlers.basehandler import BaseHandler
from src.utils.jinjautil import JINJA_ENVIRONMENT
from src.models.projectsettings import ProjectSettings, EMAIL_CHOICES

class SettingsHandler(BaseHandler):
    def get(self):
        appUser = self.appUser
        templateLocation = "templates/settings.html"
        template = JINJA_ENVIRONMENT.get_template(templateLocation)
        template_values = {
            "current_page" : "Settings",
            "logout_url"   : users.create_logout_url('/'),
            "projects"     : appUser.getAllProjects(),
            "settings"     : ProjectSettings.getSettingsByFilter(appUser),
            "app_user"     : appUser
        }
        self.response.write(template.render(template_values))

    def post(self):
        appUser = self.appUser
        for project in appUser.getAllProjects():
            emailOption = self.request.get(project.urlsafe() + "_email")
            settings = ProjectSettings.getSettingsByFilter(appUser,
                                                           project)
            if (emailOption in EMAIL_CHOICES and 
                emailOption != settings.receive_email):
                settings.receive_email = emailOption
                settings.put()
        self.response.write("Success! Your settings have been updated.")