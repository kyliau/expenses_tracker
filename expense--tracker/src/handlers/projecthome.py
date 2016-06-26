from google.appengine.api import users
from google.appengine.ext import ndb
from datetime import datetime
from src.handlers.basehandler import BaseHandler
from src.models.expense import Expense
from src.models.individualamount import IndividualAmount
from src.utils.emailutil import EmailUtil
from src.utils.jinjautil import JINJA_ENVIRONMENT

class ProjectHomeHandler(BaseHandler):
    def get(self):
        projectId = self.request.get('id')
        if not projectId:
            self.redirect('/home')
        try:
            projectKey = ndb.Key(urlsafe=projectId)
            project = projectKey.get()
        except:
            self.abort(401)
        if not project:
            self.redirect('/home')
        #user = users.get_current_user()
        #appUser = ettypes.AppUser.queryByUserId(user.user_id())
        #if not appUser or appUser.key not in project.participants:
        #    self.abort(401)
        template = JINJA_ENVIRONMENT.get_template('templates/project.html')
        template_values = {
            'current_page' : "Home",
            'project'      : project,
            'logout_url'   : users.create_logout_url('/'),
            'participants' : project.getMembers(),
            'current_user' : self.appUser
        }
        self.response.write(template.render(template_values))

    def post(self):
        encodedKey   = self.request.get('project_key')
        date         = self.request.get('date')
        amount       = float(self.request.get('amount', 0) or 0)
        details      = self.request.get('details')
        paidBy       = self.request.get('paid_by')
        #splitAll     = self.request.get('split_all')
        splitEqually = self.request.get('split_equally')
        #splitWith    = self.request.get('split_with')

        #TODO data validation!
        assert amount > 0

        projectKey = ndb.Key(urlsafe=encodedKey)
        project = projectKey.get()
        assert project

        paidByKey = ndb.Key(urlsafe=paidBy)
        assert paidByKey in project.participants

        transactionDate = datetime.strptime(date, "%Y-%m-%d")

        # TODO: abstract this out in the model instead..
        expense = Expense(parent=projectKey,
                          paid_by=paidByKey,
                          transaction_date=transactionDate,
                          details=details,
                          amount=amount,
                          split_equally=(splitEqually=="on"))
        totalAmount = 0
        for member in project.getMembers():
            amt = float(self.request.get(member.urlsafe(), 0) or 0)
            assert amt >= 0
            totalAmount += amt
            indvAmt = IndividualAmount(user=member, amount=amt)
            expense.individual_amount.append(indvAmt)
        assert abs(totalAmount - amount) < 0.01
        expense.put()
        EmailUtil.sendNewTransactionEmail(project, expense)
        self.redirect('/summary?id=' + project.key.urlsafe())