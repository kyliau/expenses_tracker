from google.appengine.ext import ndb
from google.appengine.api import users
from src.handlers.basehandler import BaseHandler
from src.models.expense import Expense
from src.utils.jinjautil import JINJA_ENVIRONMENT

class SummaryHandler(BaseHandler):
    def get(self):
        projectId = self.request.get("id")
        if not projectId:
            self.redirect("/home")
        try:
            projectKey = ndb.Key(urlsafe=projectId)
            project = projectKey.get()
        except TypeError:
            self.redirect("/home")
        if not project:
            self.redirect("/home")
        appUser = self.appUser
        if not project.isMember(appUser):
            self.abort(401)
        
        expenses = Expense.queryByProjectKey(projectKey)
        totalPaid = 0
        totalSpent = 0

        for expense in expenses:
            isPayer = expense.paid_by == appUser.key
            if isPayer:
                totalPaid += expense.amount
            amount = expense.getAmountForUser(appUser)
            totalSpent += (0 if amount is None else amount)

        amountOwed = totalSpent - totalPaid        
        message = ""
        alertType = "alert-info"
        amtString = "${:.2f}".format(abs(amountOwed))
        if abs(amountOwed) < 0.05:
            message = "All dues are clear"
            alertType = "alert-success"
        elif amountOwed > 0:
            message = "{} owes Auntie Terry {}".format(appUser.name,
                                                       amtString)
        else:
            message = "Auntie Terry owes %s %s" % (appUser.name, amtString)

        templateLocation = "templates/summary.html"
        template = JINJA_ENVIRONMENT.get_template(templateLocation)
        template_values = {
            "project_key"  : projectKey.urlsafe(),
            "message"      : message,
            "alert_type"   : alertType,
            "logout_url"   : users.create_logout_url("/"),
            "appUser"      : appUser,
            "expenses"     : expenses,
            "total_paid"   : totalPaid,
            "total_spent"  : totalSpent,
            "id_resolver"  : {m.key:m for m in project.getMembers()}
        }
        self.response.write(template.render(template_values))