from google.appengine.api import users
from google.appengine.ext import ndb
from src.handlers.basehandler import BaseHandler
from src.utils.jinjautil import JINJA_ENVIRONMENT
from src.models.appuser import AppUser
from src.models.project import Project
from src.utils.emailutil import EmailUtil
import urllib

class NewProjectHandler(BaseHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template("templates/newproject.html")
        template_values = {
            "current_page" : "Home",
            "logout_url"   : users.create_logout_url("/")
        }
        self.response.write(template.render(template_values))

    #@ndb.transactional
    def post(self):
        #user = users.get_current_user()
        #owner = ettypes.AppUser.queryByUserId(user.user_id())
        owner = self.appUser
        #if not owner:
        #    self.abort(401)

        projectName     = self.request.get("project_name")
        assert projectName
        numParticipants = int(self.request.get("num_participants", 0))
        participants    = self.request.get("participants")
        moderators      = self.request.get("moderators")
        numModerators   = int(self.request.get("num_moderators", 0))
    
        if numParticipants > 0:
            participants = participants.split(",")
            assert len(participants) == numParticipants
        else:
            participants = []
        if numModerators > 0:
            assert numModerators <= numParticipants
            moderators = moderators.split(",")
            assert len(moderators) == numModerators
            assert all(moderator in participants for moderator in moderators)
        else:
            moderators = []
        
        participants.append(owner.email)
        moderators.append(owner.email)

        # need to make sure the list is unique
        participants = list(set(participants))
        moderators = list(set(moderators))

        mapper = AppUser.mapEmailsToUsers(participants)
        participatingUsers = mapper.values()
        participantKeys = [participant.key for participant in participatingUsers]
        moderatorKeys = [mapper[moderator].key for moderator in moderators]
        #participantKeys = map(lambda user: user.key, participatingUsers)
        #moderatorKeys = map(lambda moderator: mapper[moderator].key, moderators)
        newProject = Project.addNewProject(projectName,
                                           owner.key,
                                           participantKeys,
                                           moderatorKeys)
        assert newProject

        for participant in participatingUsers:
            participant.addProject(newProject)
        ndb.put_multi(participatingUsers)

        notifyAllParticipants = self.request.get("notify_all_participants")
        if notifyAllParticipants:
            EmailUtil.sendNewProjectEmail(newProject, owner, participatingUsers)
        #settings = ettypes.Settings.createNewSettings(newProject, participatingUsers)
        #ndb.put_multi(settings)
        query_params = {
            "id" : newProject.key.urlsafe()
        }
        self.redirect("project?" + urllib.urlencode(query_params))