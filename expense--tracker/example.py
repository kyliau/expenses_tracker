import os
import urllib
import json
import ettypes

from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.ext import ndb
from datetime import datetime

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
                'current_page' : "Home",
                'logout_url'   : users.create_logout_url('/'),
                'name'         : appUser.name,
                'projects'     : appUser.getAllProjects()
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
        # potential improvement: 
        # add a query to signify where to redirect after user registers an
        # account

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
            'current_page' : "Home",
            'logout_url'   : users.create_logout_url('/')
        }
        self.response.write(template.render(template_values))

    #@ndb.transactional
    def post(self):
        user = users.get_current_user()
        owner = ettypes.AppUser.queryByUserId(user.user_id())
        if not owner:
            self.abort(401)

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

        # need to make sure the list is unique
        participants = list(set(participants))
        moderators = list(set(moderators))

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
            participant.addProject(newProject)
        ndb.put_multi(participatingUsers)
        #settings = ettypes.Settings.createNewSettings(newProject, participatingUsers)
        #ndb.put_multi(settings)
        query_params = {
            'id' : newProject.key.urlsafe()
        }
        self.redirect('project?' + urllib.urlencode(query_params))

class ProjectHome(webapp2.RequestHandler):
    def get(self):
        projectId = self.request.get('id')
        if not projectId:
            self.redirect('/home')
        try:
            projectKey = ndb.Key(urlsafe=projectId)
            project = projectKey.get()
        except:
            self.abort(401)
        if not project:
            self.redirect('/home')
        user = users.get_current_user()
        appUser = ettypes.AppUser.queryByUserId(user.user_id())
        if not appUser or appUser.key not in project.participants:
            self.abort(401)
        template = JINJA_ENVIRONMENT.get_template('templates/project.html')
        template_values = {
            'current_page' : "Home",
            'project'      : project,
            'logout_url'   : users.create_logout_url('/'),
            'participants' : project.getAllParticipants(),
            'current_user' : appUser
        }
        self.response.write(template.render(template_values))

    def post(self):
        encodedKey   = self.request.get('project_key')
        date         = self.request.get('date')
        amount       = float(self.request.get('amount', 0) or 0)
        details      = self.request.get('details')
        paidBy       = self.request.get('paid_by')
        splitAll     = self.request.get('split_all')
        splitEqually = self.request.get('split_equally')
        splitWith    = self.request.get('split_with')

        #TODO data validation!
        assert amount > 0

        projectKey = ndb.Key(urlsafe=encodedKey)
        project = projectKey.get()
        assert project

        paidByKey = ndb.Key(urlsafe=paidBy)
        assert paidByKey in project.participants

        transactionDate = datetime.strptime(date, "%Y-%m-%d")

        # TODO: abstract this out in the model instead..
        expense = ettypes.Expense(parent=projectKey,
                                  paid_by=paidByKey,
                                  transaction_date=transactionDate,
                                  details=details,
                                  amount=amount,
                                  split_equally=(splitEqually=="on"))
        totalAmount = 0
        for participant in project.participants:
            amt = float(self.request.get(participant.urlsafe(), 0) or 0)
            assert amt >= 0
            totalAmount += amt
            indvAmt = ettypes.IndividualAmount(user=participant, amount=amt)
            expense.individual_amount.append(indvAmt)
        assert abs(totalAmount - amount) < 0.01
        expense.put()
        # check if we need to send the email
        sendEmail(project, expense)
        self.redirect('/summary?id=' + project.key.urlsafe())

def sendEmail(project, expense):
    paidBy = expense.paid_by.get()
    message = mail.EmailMessage()
    message.sender = "Expense Tracker <admin@expense--tracker.appspotmail.com>"
    message.subject = "[{}] {} paid ${:.2f} for {}".format(project.name,
                                                           paidBy.name,
                                                           expense.amount,
                                                           expense.details)
    body = """
Project : {}
Date    : {}
Amount  : ${:.2f}
Details : {}
Paid By : {}
Split with :
------------""".format(project.name,
                       expense.transaction_date,
                       expense.amount,
                       expense.details,
                       paidBy.name)

    # we need to build a map of userKey to the amount of the user
    def buildMap(result, indvAmt):
        result[indvAmt.user] = indvAmt.amount
        return result
    userKeyToAmountMap = reduce(buildMap, expense.individual_amount, {})

    usersInvolved = []
    # build the message body
    for participant in project.getAllParticipants():
        assert project.key in participant.projects

        emailOption = participant.getSettingsForProject(project).receive_email
        assert emailOption in ["all", "relevant", "none"]

        amount = userKeyToAmountMap[participant.key]
        assert amount >= 0
        if amount > 0:
            body += "\n{} : ${:.2f}".format(participant.name, amount)
        isPayer = (expense.paid_by == participant.key)
        if (emailOption == "all" or
           (emailOption == "relevant" and (isPayer or amount > 0))):
            usersInvolved.append(participant)

    for appUser in usersInvolved:
            message.to = "{} <{}>".format(participant.name, participant.email)
            message.body = body
            message.html = "<pre>{}</pre>".format(body)
            message.send()

class Summary(webapp2.RequestHandler):
    def get(self):
        projectId = self.request.get('id')
        if not projectId:
            self.redirect('/home')
        try:
            projectKey = ndb.Key(urlsafe=projectId)
            project = projectKey.get()
        except TypeError:
            self.redirect('/home')
        if not project:
            self.redirect('/home')
        user = users.get_current_user()
        appUser = ettypes.AppUser.queryByUserId(user.user_id())
        if not appUser or appUser.key not in project.participants:
            self.abort(401)
        expenses = ettypes.Expense.queryByProjectKey(projectKey)
        totalPaid = 0
        totalSpent = 0
        index = project.participants.index(appUser.key)
        for expense in expenses:
            if expense.paid_by == appUser.key:
                totalPaid += expense.amount
            individualAmount = expense.individual_amount[index].amount
            totalSpent += individualAmount

        amountOwed = totalSpent - totalPaid        
        message = ''
        alertType = 'alert-info'
        amtString = "${:.2f}".format(abs(amountOwed))
        if abs(amountOwed) < 0.05:
            message = 'All dues are clear'
            alertType = 'alert-success'
        elif amountOwed > 0:
            message = "{} owes Auntie Terry {}".format(appUser.name, amtString)
        else:
            message = 'Auntie Terry owes %s %s' % (appUser.name, amtString)

        template = JINJA_ENVIRONMENT.get_template('templates/summary.html')
        template_values = {
            'project_key'  : projectKey.urlsafe(),
            'message'      : message,
            'alert_type'   : alertType,
            #'current_page' : "Home",
            'logout_url'   : users.create_logout_url('/'),
            'user_key'     : appUser.key,
            'expenses'     : expenses,
            'index'        : index,
            'total_paid'   : totalPaid,
            'total_spent'  : totalSpent,
            'id_resolver'  : project.mapIdsToUsers()
        }
        self.response.write(template.render(template_values))

class Admin(webapp2.RequestHandler):
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
        isModerator = (appUser.key in project.moderators)
        expenses = ettypes.Expense.queryByProjectKey(projectKey)
        template = JINJA_ENVIRONMENT.get_template('templates/admin.html')
        template_values = {
            'current_page' : "Admin",
            'project_key'  : projectKey.urlsafe(),
            'logout_url'   : users.create_logout_url('/'),
            'participants' : project.getAllParticipants(),
            'expenses'     : expenses,
            'id_resolver'  : project.mapIdsToUsers(),
            'is_moderator' : isModerator
        }
        self.response.write(template.render(template_values))

    def post(self):
        expenseId = self.request.get("to_delete")
        if not expenseId:
            self.response.write("Request is invalid")
        expenseKey = ndb.Key(urlsafe=expenseId)
        expense = expenseKey.get()
        if not expense:
            self.response.write("Request is invalid")
        project = expenseKey.parent().get()
        if not project:
            self.response.write("Request is invalid")
        user = users.get_current_user()
        appUser = ettypes.AppUser.queryByUserId(user.user_id())
        if appUser.key not in project.moderators:
            self.abort(401, detail="User is not authorized")
        expenseKey.delete()
        print expense
        self.response.write("Deleted " + expense.details)

class Settings(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        appUser = ettypes.AppUser.queryByUserId(user.user_id())
        if not appUser:
            self.abort(401)
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
        user = users.get_current_user()
        appUser = ettypes.AppUser.queryByUserId(user.user_id())
        if not appUser:
            self.abort(401)
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

app = webapp2.WSGIApplication([
    ('/home', MainPage),
    ('/register', RegisterNewUser),
    ('/newproject', CreateNewProject),
    ('/project', ProjectHome),
    ('/summary', Summary),
    ('/admin', Admin),
    ('/settings', Settings)
], debug=True)

