from google.appengine.api import users
from src.handlers.basehandler import BaseHandler
from src.utils.jinjautil import JINJA_ENVIRONMENT
from src.models.projectsettings import ProjectSettings, EMAIL_CHOICES

class SettingsHandler(BaseHandler):
    def get(self):
        """
        Show the settings page for all projects.
        """
        appUser = self.appUser
        templateLocation = "templates/settings.html"
        template = JINJA_ENVIRONMENT.get_template(templateLocation)
        template_values = {
            "current_page" : "Settings",
            "logout_url"   : users.create_logout_url('/'),
            "projects"     : appUser.getAllProjects(),
            "settings"     : ProjectSettings.getUserSettings(appUser),
            "app_user"     : appUser
        }
        self.response.write(template.render(template_values))

    def post(self):
        """
        Update user email settings for all projects.
        """
        appUser = self.appUser
        for project in appUser.getAllProjects():
            newChoice = self.request.get(project.key.urlsafe() + "_email")
            settings = ProjectSettings.getUserSettingsForProject(appUser,
                                                                 project)
            existingChoice = settings.receive_email
            if (newChoice in EMAIL_CHOICES and newChoice != existingChoice):
                settings.receive_email = newChoice
                settings.put()
        self.response.write("Success! Your settings have been updated.")