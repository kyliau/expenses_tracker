from google.appengine.ext import ndb
from google.appengine.api import users
from src.handlers.basehandler import BaseHandler
from src.models.expense import Expense
from src.utils.jinjautil import JINJA_ENVIRONMENT

class SummaryHandler(BaseHandler):
    def get(self):
        projectId = self.request.get('id')
        if not projectId:
            self.redirect('/home')
        try:
            projectKey = ndb.Key(urlsafe=projectId)
            project = projectKey.get()
        except TypeError:
            self.redirect('/home')
        if not project:
            self.redirect('/home')
        appUser = self.appUser
        if appUser.key not in project.participants:
            self.abort(401)
        
        expenses = Expense.queryByProjectKey(projectKey)
        totalPaid = 0
        totalSpent = 0
        index = project.participants.index(appUser.key)
        for expense in expenses:
            if expense.paid_by == appUser.key:
                totalPaid += expense.amount
            individualAmount = expense.individual_amount[index].amount
            totalSpent += individualAmount

        amountOwed = totalSpent - totalPaid        
        message = ''
        alertType = 'alert-info'
        amtString = "${:.2f}".format(abs(amountOwed))
        if abs(amountOwed) < 0.05:
            message = 'All dues are clear'
            alertType = 'alert-success'
        elif amountOwed > 0:
            message = "{} owes Auntie Terry {}".format(appUser.name, amtString)
        else:
            message = 'Auntie Terry owes %s %s' % (appUser.name, amtString)

        template = JINJA_ENVIRONMENT.get_template('templates/summary.html')
        template_values = {
            'project_key'  : projectKey.urlsafe(),
            'message'      : message,
            'alert_type'   : alertType,
            #'current_page' : "Home",
            'logout_url'   : users.create_logout_url('/'),
            'user_key'     : appUser.key,
            'expenses'     : expenses,
            'index'        : index,
            'total_paid'   : totalPaid,
            'total_spent'  : totalSpent,
            'id_resolver'  : project.mapIdsToUsers()
        }
        self.response.write(template.render(template_values))