import os
import urllib
import json
import ettypes

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        appUser = ettypes.AppUser.queryByUserId(user.user_id())
        if appUser:
            projects = appUser.getAllProjects()
            template_values = {
                'logout_url' : users.create_logout_url('/'),
                'name'       : appUser.name,
                'projects'   : appUser.getAllProjects()
            }
            template = JINJA_ENVIRONMENT.get_template('templates/home.html')
            self.response.write(template.render(template_values))
        else:
            self.redirect('/register')

class RegisterNewUser(webapp2.RequestHandler):
    def get(self):
        # need to check if user is actually registered
        template = JINJA_ENVIRONMENT.get_template('templates/register.html')
        self.response.write(template.render())

    def post(self):
        user = users.get_current_user()
        assert user is not None
        name = self.request.get('name', '')
        assert name
        newUser = ettypes.AppUser.addRegisteredUser(user=user, name=name)
        assert newUser
        self.redirect('/home')

class CreateNewProject(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/newproject.html')
        template_values = {
            'logout_url' : users.create_logout_url('/')
        }
        self.response.write(template.render(template_values))

    def post(self):
        user = users.get_current_user()
        owner = ettypes.AppUser.queryByUserId(user.user_id())
        assert owner

        projectName     = self.request.get('project_name')
        numParticipants = float(self.request.get('num_participants', 0))
        participants    = self.request.get('participants')
        moderators      = self.request.get('moderators')
        numModerators   = float(self.request.get('num_moderators', 0))
        assert projectName
        if numParticipants > 0:
            participants = participants.split(',')
            assert len(participants) == numParticipants
        else:
            participants = []
        if numModerators > 0:
            assert numModerators <= numParticipants
            moderators = moderators.split(',')
            assert len(moderators) == numModerators
            assert all(moderator in participants for moderator in moderators)
        else:
            moderators = []
        participants.append(owner.email)
        moderators.append(owner.email)

        mapper = ettypes.AppUser.mapEmailsToUsers(participants)
        participatingUsers = mapper.values()
        participantKeys = map(lambda user: user.key, participatingUsers)
        moderatorKeys = map(lambda moderator: mapper[moderator].key, moderators)
        newProject = ettypes.Project.addNewProject(projectName,
                                                   owner.key,
                                                   participantKeys,
                                                   moderatorKeys)
        assert newProject
        for participant in participatingUsers:
            participant.projects.append(newProject.key)
        ndb.put_multi(participatingUsers)
        self.redirect('/home')

class ProjectHome(webapp2.RequestHandler):
    def get(self):
        projectId = self.request.get('id')
        if not projectId:
            self.redirect('/home')
        projectKey = ndb.Key(urlsafe=projectId)
        project = projectKey.get()
        if not project:
            self.redirect('/home')
        user = users.get_current_user()
        appUser = ettypes.AppUser.queryByUserId(user.user_id())
        if not appUser or appUser.key not in project.participants:
            self.abort(401)
        template = JINJA_ENVIRONMENT.get_template('templates/project.html')
        template_values = {
            'logout_url' : users.create_logout_url('/'),
            'participants' : project.getAllParticipants()
        }
        self.response.write(template.render(template_values))

class Transaction(webapp2.RequestHandler):
    def post(self):
        pass


app = webapp2.WSGIApplication([
    ('/home', MainPage),
    ('/register', RegisterNewUser),
    ('/newproject', CreateNewProject),
    ('/project', ProjectHome),
    ('/submit', Transaction)
], debug=True)

