from google.appengine.ext import ndb
from src.models.appuser import AppUser
from src.models.projectsettings import ProjectSettings

class ProjectMember(ndb.Model):
    """
    A model to represent a member in a project.
    """

    user_key = ndb.KeyProperty(kind=AppUser, required=True)
    is_admin = ndb.BooleanProperty(default=False)
    settings = ndb.StructuredProperty(ProjectSettings,
                                      default=ProjectSettings())