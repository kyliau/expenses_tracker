from google.appengine.ext import ndb
from src.models.appuser import AppUser

class ProjectSettings(ndb.Model):
    """
    A model to represent project settings for a particular user.
    """
    user_key = ndb.KeyProperty(kind=AppUser,
                               indexed=True,
                               required=True)
    receive_email = ndb.StringProperty(choices=["all",
                                                "relevant",
                                                "none"],
                                       default="relevant")

    @classmethod
    def create(cls, project, user):
        """
        Return a new instance of 'ProjectSettings' for the specified
        'project' and 'user'. Note the new instance is not commited to
        the datastore.
        """
        return cls(
            parent=project.key,
            user_key=user.key
        )

    @classmethod
    def getSettings(cls, project, user):
        """
        Return the first 'ProjectSettings' that matches the specified
        'project' and 'user'.
        """
        query = cls.query(ancestor=project.key,
                          filters=ProjectSettings.user_key==user.key)
        return query.get()