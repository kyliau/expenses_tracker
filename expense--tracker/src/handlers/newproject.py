import urllib
import json
from google.appengine.api import users
from google.appengine.ext import ndb
from src.handlers.basehandler import BaseHandler
from src.utils.jinjautil import JINJA_ENVIRONMENT
from src.models.appuser import AppUser
from src.models.project import Project
from src.utils.emailutil import EmailUtil

class NewProjectHandler(BaseHandler):
    def get(self):
        """
        Return the new project page
        """ 
        template = JINJA_ENVIRONMENT.get_template("templates/newproject.html")
        template_values = {
            "current_page" : "Home",
            "logout_url"   : users.create_logout_url("/")
        }
        self.response.write(template.render(template_values))

    #@ndb.transactional
    def post(self):
        """
        """
        # TODO: data validation
        projectName = self.request.get("project_name", "My Project")
        notifyAllParticipants = self.request.get("notify_all_participants")
        # TODO: wrap in try catch
        participants = json.loads(self.request.get("participants"))

        owner = self.appUser
        participants.append({
            "email"       : owner.email,
            "isModerator" : True
        })
        
        # need to make sure the list is unique
        # instead of overriding participants we should throw an error
        #participants = {p["email"]:p for p in participants}.values()

        appUsers = [AppUser.create(p["email"]) for p in participants]
        keys = [user.key for user in appUsers]
        self.response.write("Before " + str(keys))
        userKeys = ndb.put_multi(appUsers)
        self.response.write("After " + str(userKeys))
        

        #participantKeys = ndb.Model.put_multi([])
        #mapper = AppUser.mapEmailsToUsers(participants)
        #participatingUsers = mapper.values()
        #participantKeys = [participant.key for participant in participatingUsers]
        #moderatorKeys = [mapper[moderator].key for moderator in moderators]
        #participantKeys = map(lambda user: user.key, participatingUsers)
        #moderatorKeys = map(lambda moderator: mapper[moderator].key, moderators)
        
        #newProject = Project.addNewProject(projectName,
        #                                   owner.key,
        #                                   participantKeys,
        #                                   moderatorKeys)
        #assert newProject

        #for participant in participatingUsers:
        #    participant.addProject(newProject)
        #ndb.put_multi(participatingUsers)

        
        #if notifyAllParticipants:
        #    EmailUtil.sendNewProjectEmail(newProject, owner, participatingUsers)
        
        #settings = ettypes.Settings.createNewSettings(newProject, participatingUsers)
        #ndb.put_multi(settings)
        
        #query_params = {
        #    "id" : newProject.key.urlsafe()
        #}
        #self.redirect("project?" + urllib.urlencode(query_params))