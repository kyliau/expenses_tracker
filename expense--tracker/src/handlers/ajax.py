from google.appengine.ext import ndb
from src.handlers.basehandler import BaseHandler

# This class handles all ajax requests
class AjaxHandler(BaseHandler):
    # This handles the delete transaction request
    def post(self):
        expenseId = self.request.get("to_delete")
        if not expenseId:
            # TODO: Consider abort with an error code here
            return self.response.write("Request is invalid")
        # TODO: The statement below might throw due to invalid key.
        # Need to double check the API
        expenseKey = ndb.Key(urlsafe=expenseId)
        expense = expenseKey.get()
        if not expense:
            self.response.write("Request is invalid")
        project = expenseKey.parent().get()
        if not project:
            self.response.write("Request is invalid")
        if project.isAdmin(self.appUser):
            expenseKey.delete()
            self.response.write("Deleted " + expense.details)
        else:
            self.abort(401, detail="User is not authorized")