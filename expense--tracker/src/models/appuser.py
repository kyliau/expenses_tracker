from google.appengine.ext import ndb
#from src.models.projectsettings import ProjectSettings

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

class AppUser(ndb.Model):
    name          = ndb.StringProperty(required=True)
    email         = ndb.StringProperty(required=True, indexed=True)
    last_update   = ndb.DateTimeProperty(auto_now=True)
    creation_date = ndb.DateTimeProperty(auto_now_add=True)
    projects      = ndb.KeyProperty(kind="Project", repeated=True)
    user_id       = ndb.StringProperty(indexed=True)

    @classmethod
    def queryByUserId(cls, user_id):
        """Return the AppUser that has the specified 'user_id'.
           Return None if there is no such AppUser."""
        query = cls.query(ancestor=APPUSER_PARENT_KEY,
                          filters=AppUser.user_id==user_id)
        return query.get()

    @classmethod
    def queryByEmail(cls, email):
        """
        Return the AppUser that has the specified 'email'.
        Return None if there is no such AppUser.
        """
        query = cls.query(ancestor=APPUSER_PARENT_KEY,
                          filters=AppUser.email==email)
        return query.get()

    @classmethod
    def create(cls, email, name=None):
        """
        Return a new instance of 'AppUser' with the specified 'email'
        and optional 'name'. If 'name'' is not specified then the
        username of the 'email' is used instead.
        If there is an existing user with the specified 'email' then
        return the existing instance instead.
        Note that this method does not commit the new instance to the
        datastore.
        """
        existingUser = cls.queryByEmail(email.lower())
        if existingUser:
            return existingUser
        else:
            if name is None:
                name = email.lower().split("@")[0]
            return cls(parent=APPUSER_PARENT_KEY,
                       name=name,
                       email=email.lower())

    def isNew(self):
        """
        Return true if the 'user_id' of the user is defined, otherwise
        return false.
        """
        return self.user_id is None

    def getAllProjects(self):
        """
        Return all the projects for which the user is a member of.
        """
        return ndb.get_multi(self.projects)

    def addProject(self, project):
        """
        Add the specified 'project' to the user's list of 'projects'.
        """
        self.projects.append(project.key)

    def deleteProject(self, project):
        """
        Delete the specified 'project' from the user list of projects.
        Note this method is meant to delete the entire project, not to
        remove the user from the specified 'project'. The changes is
        not committed to the datastore. Return true if the 'project' is
        successfully removed from the list, false otherwise.
        """
        try:
            index = self.projects.index(project.key)
            self.projects.pop(index)
            return True
        except ValueError:
            return False
