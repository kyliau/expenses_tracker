from google.appengine.ext import ndb
from src.models.appuser import AppUser

class IndividualAmount(ndb.Model):
    user_key = ndb.KeyProperty(kind=AppUser, required=True)
    amount = ndb.FloatProperty(required=True)