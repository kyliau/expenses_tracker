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
        participants = self.request.get("participants")
        # TODO: wrap in try catch
        members = json.loads(participants)

        owner = self.appUser
        members.append({
            "email"   : owner.email,
            "isAdmin" : True
        })
        
        # need to make sure the list is unique
        # instead of overriding participants we should throw an error
        #participants = {p["email"]:p for p in participants}.values()

        appUsers = [AppUser.create(m["email"]) for m in members]
        ndb.put_multi(appUsers)
        
        for member, appUser in zip(members, appUsers):
            member["key"]   = appUser.key
            member["name"]  = appUser.name
            member["email"] = appUser.email

        project = Project.create(projectName, owner, members)
        project.put()

        for appUser in appUsers:
            appUser.addProject(project)
        
        ndb.put_multi(appUsers)

        if notifyAllParticipants == "on":
            EmailUtil.sendNewProjectEmail(project, owner, members)
        
        query_params = {
            "id" : project.key.urlsafe()
        }
        self.redirect("project?" + urllib.urlencode(query_params))