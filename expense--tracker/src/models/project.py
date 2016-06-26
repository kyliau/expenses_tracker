from google.appengine.ext import ndb
from src.models.appuser import AppUser
from src.models.projectmember import ProjectMember

PROJECT_PARENT_KEY = ndb.Key("Project", "DEFAULT_KEY")

class Project(ndb.Model):
    """
    A model for a project that has a name, an owner, and a list of
    members.
    """
    name = ndb.StringProperty(required=True)
    owner = ndb.KeyProperty(kind=AppUser,
                            indexed=True,
                            required=True)
    creation_date = ndb.DateTimeProperty(auto_now_add=True)
    last_update   = ndb.DateTimeProperty(auto_now=True)
    members       = ndb.StructuredProperty(ProjectMember,
                                           repeated=True)

    @classmethod
    def create(cls, name, owner, members):
        """
        Return a new 'Project' instance with the specified 'name',
        'owner', and 'members'. Note that the new instance is not
        committed to the datastore.
        """
        return cls(
            parent=PROJECT_PARENT_KEY,
            name=name,
            owner=owner.key,
            members=[ProjectMember(
                user_key=member["key"],
                is_admin=member["isAdmin"]
            ) for member in members])

    def getMembers(self):
        """
        Return the members as 'AppUser' instances in this project.
        """
        keys = [member.user_key for member in self.members]
        return ndb.get_multi(keys)

    def isMember(self, user):
        """
        Return true if the specified 'user' is a member of this
        project, otherwise return false.
        """
        keys = [member.user_key for member in self.members]
        return user.key in keys

    def isAdmin(self, user):
        """
        Return true if the specified 'user' is an admin of this project,
        otherwise return false.
        """
        keys = [member.user_key for member in self.members if member.is_admin]
        return user.key in keys

    def getSettings(self, user):
        """
        Return the 'ProjectSettings' for the specified 'user' if
        'user' is a member of this project, otherwise return None.
        """
        for member in self.members:
            if member.user_key == user.key:
                return member.settings
        return None

    #def mapIdsToUsers(self):
    #    return dict(zip(self.participants, self.getAllParticipants()))

