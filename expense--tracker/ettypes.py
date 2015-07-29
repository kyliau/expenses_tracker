import urllib
from google.appengine.ext import ndb

# Note: Every user has the same user ID for all App Engine applications.
# If your app uses the user ID in public data, such as by including it in a
# URL parameter, you should use a hash algorithm with a "salt" value added
# to obscure the ID. Exposing raw IDs could allow someone to associate a
# user's activity in one app with that in another, or get the user's email
# address by coercing the user to sign in to another app.
#
# The User service API can return the current user's information as a User
# object. Although User objects can be stored as a property value in the
# datastore, we strongly recommend that you avoid doing so because this
# includes the email address along with the user's unique ID.
# If a user changes their email address and you compare their old, stored
# User to the new User value, they won't match. Instead, consider using the
# User user ID value as the user's stable unique identifier.

# If user_is None, user is not registered.

APPUSER_PARENT_KEY = ndb.Key("AppUser", "DEFAULT_KEY")
PROJECT_PARENT_KEY = ndb.Key("Project", "DEFAULT_KEY")

class AppUser(ndb.Model):
    name          = ndb.StringProperty(required=True)
    email         = ndb.StringProperty(required=True)
    last_update   = ndb.DateTimeProperty(auto_now=True)
    creation_date = ndb.DateTimeProperty(auto_now_add=True)
    projects      = ndb.KeyProperty(kind='Project', repeated=True)
    user_id       = ndb.StringProperty(indexed=True)
    encoded_key   = ndb.StringProperty(indexed=True, required=True)

    @classmethod
    def queryByUserId(cls, user_id):
        query = cls.query(ancestor=APPUSER_PARENT_KEY,
                          filters=AppUser.user_id==user_id)
        return query.get()

    @classmethod
    def queryByEmail(cls, email):
        query = cls.query(ancestor=APPUSER_PARENT_KEY,
                          filters=AppUser.email==email)
        return query.get()

    @classmethod
    def createUnregisteredUser(cls, email):
        #newId = cls.allocate_ids(size=1)[0]
        #userKey = ndb.Key(cls, newId, parent=APPUSER_PARENT_KEY)
        name = email.split('@')[0]
        return cls(parent=APPUSER_PARENT_KEY,
                   key=userKey,
                   name=name,
                   email=email,
                   encoded_key=userKey.urlsafe())

    @classmethod
    def addRegisteredUser(cls, user, name):
        appUser = cls.queryByEmail(user.email())
        if appUser:
            assert appUser.user_id is None
            appUser.name    = name
            appUser.user_id = user.user_id()
        else:
            appUser = cls.createUnregisteredUser(user.email())
            appUser.populate(user_id=user.user_id(), name=name)
        appUser.put()
        return appUser

    @classmethod
    def mapEmailsToUsers(cls, emails):
        mapper = {}
        for email in emails:
            appUser = cls.queryByEmail(email)
            if appUser is None:
                appUser = cls.createUnregisteredUser(email)
            assert appUser
            mapper[email] = appUser
        return mapper

    def getAllProjects(self):
        return ndb.get_multi(self.projects)

class Project(ndb.Model):
    name          = ndb.StringProperty(required=True)
    url           = ndb.StringProperty()
    owner         = ndb.KeyProperty(kind=AppUser, indexed=True, required=True)
    creation_date = ndb.DateTimeProperty(auto_now_add=True)
    last_update   = ndb.DateTimeProperty(auto_now=True)
    participants  = ndb.KeyProperty(kind=AppUser, repeated=True)
    moderators    = ndb.KeyProperty(kind=AppUser, repeated=True)

    @classmethod
    def addNewProject(cls, name, owner, participants, moderators):
        newId = cls.allocate_ids(size=1)[0]
        projectKey = ndb.Key(cls, newId, parent=PROJECT_PARENT_KEY)
        query_params = {'id': projectKey.urlsafe()}
        projectUrl = urllib.urlencode(query_params);
        newProject = cls(key=projectKey,
                         name=name,
                         url=projectUrl,
                         owner=owner,
                         participants=participants,
                         moderators=moderators)
        newProject.put()
        return newProject

    def getAllParticipants(self):
        return ndb.get_multi(self.participants)

    def mapIdsToUsers(self):
        return dict(zip(self.participants, self.getAllParticipants()))

class IndividualAmount(ndb.Model):
    user   = ndb.KeyProperty(kind=AppUser, indexed=False, required=True)
    amount = ndb.FloatProperty(indexed=False, required=True)

class Expense(ndb.Model):
    paid_by           = ndb.KeyProperty(kind=AppUser, required=True)
    creation_date     = ndb.DateTimeProperty(auto_now_add=True)
    last_update       = ndb.DateTimeProperty(auto_now=True)
    transaction_date  = ndb.DateProperty(indexed=True, required=True)
    details           = ndb.StringProperty(required=True)
    amount            = ndb.FloatProperty(required=True)
    split_equally     = ndb.BooleanProperty(default=False)
    individual_amount = ndb.StructuredProperty(IndividualAmount, repeated=True)

    @classmethod
    def addNewExpense(cls, paidBy, date, details, amount, splitEqually):
        return cls(paid_by=paidBy,
                   transaction_date=date,
                   details=details,
                   amount=amount,
                   split_equally=splitEqually)

    @classmethod
    def queryByProjectKey(cls, projectKey):
        query = cls.query(ancestor=projectKey).order(-Expense.transaction_date,
                                                     -Expense.last_update)
        return query.fetch()

class Settings(ndb.Model):
    #project       = ndb.KeyProperty(kind=Project, required=True)
    #user          = ndb.KeyProperty(kind=AppUser, required=True)
    receive_email = ndb.StringProperty(choices=['all', 'relevant', 'none'],
                                       default='none')

    @classmethod
    def addNewSetting(cls, project, appUser):
        projectKey = project.key
        appUserKey = appUser.key
        setting = cls(parent=ndb.Key(flat=projectKey.flat(), parent=appUserKey))
        setting.put()
        return setting

    @classmethod
    def getAllSettings(cls, appUser):
        appUserKey = appUser.key
        query = cls.query(ancestor=appUserKey)
        return query.fetch()

