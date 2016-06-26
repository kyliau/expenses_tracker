from google.appengine.ext import ndb

class ProjectSettings(ndb.Model):
    """
    A model to represent project settings for a particular user.
    """
    receive_email = ndb.StringProperty(choices=["all",
                                                "relevant",
                                                "none"],
                                       default="relevant")
