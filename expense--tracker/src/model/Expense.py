from google.appengine.ext import ndb

class IndividualAmount(ndb.Model):
    user   = ndb.KeyProperty(kind=AppUser, indexed=False, required=True)
    amount = ndb.FloatProperty(indexed=False, required=True)

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
        ndb.delete_multi(cls.query(ancestor=project.key).iter(keys_only = True))

    @classmethod
    def queryByProjectKey(cls, projectKey):
        query = cls.query(ancestor=projectKey).order(-Expense.transaction_date,
                                                     -Expense.last_update)
        return query.fetch()

