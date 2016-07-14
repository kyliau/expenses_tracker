from google.appengine.ext import ndb
#from src.models.project import Project

EMAIL_CHOICES = ["all", "relevant", "none"]
DEFAULT_EMAIL_CHOICE = "relevant"

class ProjectSettings(ndb.Model):
    """
    A model to represent project settings for a particular user.
    """
    project_key = ndb.KeyProperty(kind="Project",
                                  indexed=True,
                                  required=True)
    receive_email = ndb.StringProperty(choices=EMAIL_CHOICES,
                                       default=DEFAULT_EMAIL_CHOICE)

    @classmethod
    def create(cls, user, project):
        """
        Return a new instance of 'ProjectSettings' for the specified
        'project' and 'user'. Note the new instance is not commited to
        the datastore.
        """
        return cls(
            parent=user.key,
            project_key=project.key
        )

    @classmethod
    def getUserSettings(cls, user):
        """
        Return all ProjectSettings for the specified 'user'.
        """
        query = cls.query(ancestor=user.key)
        return query.fetch()

    @classmethod
    def getUserSettingsForProject(cls, user, project):
        """
        Return the ProjectSettings for the specified 'user' and
        'project'. Return None if it does not exist.
        """
        query = cls.query(ancestor=user.key,
                          filters=ProjectSettings.project_key==project.key)
        return query.get()