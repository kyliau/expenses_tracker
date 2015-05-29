# processpayment.py

import datetime
import jinja2
import cgi
import json
import os
import webapp2

from google.appengine.ext import ndb
from google.appengine.api import mail

DEFAULT_EXPENSE = 'default_expense'

def expense_key(expense_name=DEFAULT_EXPENSE):
    """ Constructs a Datastore key for Expense entity
        We use expense_name as the key
    """
    return ndb.Key('Expense', expense_name)

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class Expense(ndb.Model):
    """ A main model for representing an individual expense entry """
    createdDate = ndb.DateTimeProperty(auto_now_add=True)
    transactionDate = ndb.DateTimeProperty(indexed=True)
    details = ndb.StringProperty(indexed=False)
    amount = ndb.FloatProperty(indexed=False)
    kaiAmount = ndb.FloatProperty(indexed=False)
    keenAmount = ndb.FloatProperty(indexed=False)
    paidBy = ndb.StringProperty(indexed=False)

class MainPage(webapp2.RequestHandler):
    def get(self): 
        template = jinja_environment.get_template('template.html')
        self.response.out.write(template.render())

class ExpenseTracker(webapp2.RequestHandler):
    def post(self):
        expense = Expense(parent=expense_key(DEFAULT_EXPENSE))
        expense.details = self.request.get('details').strip()
        expense.transactionDate = datetime.datetime.strptime(self.request.get('date'), "%Y-%m-%d")
        expense.amount = float(self.request.get('amount', 0))
        expense.kaiAmount = float(self.request.get('kaiAmount', 0))
        expense.keenAmount = float(self.request.get('keenAmount', 0))
        expense.paidBy = self.request.get('paidBy')
        expense.put()
        sendSummaryEmail(expense)
        #self.response.headers['Content-Type'] = 'text/plain'
        #self.response.write("Successfully added expense!")
        self.redirect('/admin')

def sendSummaryEmail(expense):
    message = mail.EmailMessage()
    message.sender = "Expenses Tracker <admin@genuine-flight-91402.appspotmail.com>"
    message.subject = "{} paid ${:.2f} for {}".format(expense.paidBy,
                                                      expense.amount,
                                                      expense.details)
    message.body = """
    Date        : {}
    Amount      : ${:.2f}
    Details     : {}
    Paid By     : {}
    Kai Amount  : ${:.2f}
    Keen Amount : ${:.2f}
    """.format(expense.transactionDate,
               expense.amount,
               expense.details,
               expense.paidBy,
               expense.kaiAmount,
               expense.keenAmount)
    message.to = "Kai Boon Ee <eekaiboon@gmail.com>"
    message.send()
    message.to = "Keen Yee Liau <kyliau@gmail.com>"
    message.send()

class Admin(webapp2.RequestHandler):
    def get(self):
        expenses_query = Expense.query(
            ancestor=expense_key(DEFAULT_EXPENSE)).order(-Expense.transactionDate, -Expense.createdDate)
        expenses = expenses_query.fetch()

        paidByKai = 0
        sharedByKai = 0
        for expense in expenses:
            if (expense.paidBy == 'Kai'):
                paidByKai += expense.amount
            sharedByKai += expense.kaiAmount

        oweToKai = paidByKai - sharedByKai
        
        message = ''
        alertType = 'alert-info'
        if abs(oweToKai) < 0.05:
            message = 'All dues are clear'
            alertType = 'alert-success'
        elif oweToKai < 0:
            message = 'Kai owes Keen USD ' + "{:10.2f}".format(abs(oweToKai))
        else:
            message = 'Keen owes Kai USD ' + "{:10.2f}".format(oweToKai)

        template = jinja_environment.get_template('admin.html')
        self.response.out.write(template.render({'expenses':expenses, 'alertType':alertType, 'message':message}))

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/submit', ExpenseTracker),
    ('/admin', Admin),
], debug=True)

