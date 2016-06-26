from google.appengine.ext import ndb

class Settings(ndb.Model):
    #project       = ndb.KeyProperty(kind=Project, required=True)
    #user          = ndb.KeyProperty(kind=AppUser, required=True)
    receive_email = ndb.StringProperty(choices=['all', 'relevant', 'none'],
                                       default='relevant')

    @classmethod
    def createNewSettings(cls, project, appUsers):
        def createNewSetting(appUser):
            key = ndb.Key(flat=project.key.flat(), parent=appUser.key)
            return cls(parent=key)
        return map(createNewSetting, appUsers)

