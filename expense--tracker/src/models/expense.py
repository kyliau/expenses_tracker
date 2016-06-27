from google.appengine.ext import ndb
from src.models.appuser import AppUser
from src.models.individualamount import IndividualAmount

class Expense(ndb.Model):
    paid_by           = ndb.KeyProperty(kind=AppUser, required=True)
    creation_date     = ndb.DateTimeProperty(auto_now_add=True)
    last_update       = ndb.DateTimeProperty(auto_now=True)
    transaction_date  = ndb.DateProperty(indexed=True, required=True)
    details           = ndb.StringProperty(required=True)
    amount            = ndb.FloatProperty(required=True)
    split_equally     = ndb.BooleanProperty(default=False)
    individual_amount = ndb.StructuredProperty(IndividualAmount, repeated=True)

    #@classmethod
    #def addNewExpense(cls, paidBy, date, details, amount, splitEqually):
    #    return cls(paid_by=paidBy,
    #               transaction_date=date,
    #               details=details,
    #               amount=amount,
    #               split_equally=splitEqually)

    @classmethod
    def deleteAllExpensesInProject(cls, project):
        keys = (cls.query(ancestor=project.key)
                   .iter(keys_only = True))
        ndb.delete_multi(keys)

    @classmethod
    def queryByProject(cls, project):
        query = (cls.query(ancestor=project.key)
                    .order(-Expense.transaction_date,
                           -Expense.last_update))
        return query.fetch()

    def getAmountForUser(self, user):
        """
        Return the amount of the specified 'user' if 'user' is involved
        in this Expense, otherwise return None.
        """
        return next((ia.amount for ia in self.individual_amount
                               if ia.user_key == user.key), None)

