from google.appengine.ext import ndb
from src.models.appuser import AppUser

class IndividualAmount(ndb.Model):
    user   = ndb.KeyProperty(kind=AppUser, indexed=False, required=True)
    amount = ndb.FloatProperty(indexed=False, required=True)