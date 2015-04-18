# processpayment.py

import jinja2
import cgi
import json
import os
import webapp2

from google.appengine.ext import ndb

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
    date = ndb.DateTimeProperty(auto_now_add=True)
    details = ndb.StringProperty(indexed=False)
    amount = ndb.FloatProperty(indexed=False)
    kaiAmount = ndb.FloatProperty(indexed=False)
    keenAmount = ndb.FloatProperty(indexed=False)
    paidBy = ndb.StringProperty(indexed=False)

class ExpenseEntry:
    def __init__(self, details, amount, paidBy):
         self.details = details
         self.amount = amount
         self.paidBy = paidBy

class MainPage(webapp2.RequestHandler):
    def get(self): 
        template = jinja_environment.get_template('template.html')
        self.response.out.write(template.render())

class ExpenseTracker(webapp2.RequestHandler):
    def post(self):
        print self.request
        expense = Expense(parent=expense_key(DEFAULT_EXPENSE))
        expense.details = self.request.get('details')
        expense.amount = float(self.request.get('amount', 0))
        expense.kaiAmount = float(self.request.get('kaiAmount', 0))
        expense.keenAmount = float(self.request.get('keenAmount', 0))
        expense.paidBy = self.request.get('paidBy')
        expense.put()
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write("Successfully added expense!")
        #self.redirect('/')

class Admin(webapp2.RequestHandler):
    def get(self):
        expenses_query = Expense.query(
            ancestor=expense_key(DEFAULT_EXPENSE)).order(-Expense.date)
        expenses = expenses_query.fetch()

        paidByKai = 0
        sharedByKai = 0
        for expense in expenses:
            if (expense.paidBy == 'Kai'):
                paidByKai += expense.amount
            sharedByKai += expense.kaiAmount

        oweToKai = paidByKai - sharedByKai
        
        message = ''
        if (oweToKai < 0):
            message = 'Kai owes Keen USD ' + "{:10.2f}".format(abs(oweToKai))
        else:
            message = 'Keen owes Kai USD ' + "{:10.2f}".format(oweToKai)
        print message

        template = jinja_environment.get_template('admin.html')
        self.response.out.write(template.render({'expenses':expenses, 'message':message}))

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/submit', ExpenseTracker),
    ('/admin', Admin),
], debug=True)

