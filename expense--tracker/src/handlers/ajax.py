# This class handles all ajax requests
class RequestProcessor(webapp2.RequestHandler):
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
        user = users.get_current_user()
        appUser = ettypes.AppUser.queryByUserId(user.user_id())
        if appUser.key not in project.moderators:
            self.abort(401, detail="User is not authorized")
        expenseKey.delete()
        self.response.write("Deleted " + expense.details)