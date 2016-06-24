from google.appengine.ext import ndb

PROJECT_PARENT_KEY = ndb.Key("Project", "DEFAULT_KEY")

class Project(ndb.Model):
    name          = ndb.StringProperty(required=True)
    owner         = ndb.KeyProperty(kind=AppUser, indexed=True, required=True)
    creation_date = ndb.DateTimeProperty(auto_now_add=True)
    last_update   = ndb.DateTimeProperty(auto_now=True)
    participants  = ndb.KeyProperty(kind=AppUser, repeated=True)
    moderators    = ndb.KeyProperty(kind=AppUser, repeated=True)

    @classmethod
    def addNewProject(cls, name, owner, participants, moderators):
        newProject = cls(parent=PROJECT_PARENT_KEY,
                         name=name,
                         owner=owner,
                         participants=participants,
                         moderators=moderators)
        newProject.put()
        return newProject

    def getAllParticipants(self):
        return ndb.get_multi(self.participants)

    def mapIdsToUsers(self):
        return dict(zip(self.participants, self.getAllParticipants()))

