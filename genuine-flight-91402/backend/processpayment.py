import cgi
import json

from google.appengine.ext import ndb

import webapp2

DEFAULT_EXPENSE = 'default_expense'

def expense_key(expense_name=DEFAULT_EXPENSE):
	""" Constructs a Datastore key for Expense entity
		We use expense_name as the key
	"""
	return ndb.Key('Expense', expense_name)

class Expense(ndb.Model):
	""" A main model for representing an individual expense entry """
	date = ndb.DateTimeProperty(auto_now_add=True)
	details = ndb.StringProperty(indexed=False)
	amount = ndb.FloatProperty(indexed=False)
	amountKai = ndb.FloatProperty(indexed=False)
	amountKeen = ndb.FloatProperty(indexed=False)
	paidBy = ndb.StringProperty(indexed=False)

class ExpenseEntry:
	def __init__(self, details, amount, paidBy):
 		self.details = details
 		self.amount = amount
 		self.paidBy = paidBy

class MainPage(webapp2.RequestHandler):

    def post(self):
        expense = Expense(parent=expense_key(DEFAULT_EXPENSE))
        expense.details = self.request.get('details')
        expense.amount = self.request.get('amount', 0)
        expense.amountKai = self.request.get('amountKai', 0)
        expense.amountKeen = self.request.get('amountKeen', 0)
        expense.paidBy = self.request.get('paidBy')
        expense.put()

    def get(self):
        expenses_query = Expense.query(
        	ancestor=expense_key(DEFAULT_EXPENSE)).order(-Expense.date)
        expenses = expenses_query.fetch(10)

        for expense in expenses:
            print str(expense)
            '''
        	expense_entry = str(expense.date) + ' ' + expense.details + ' ' + str(expense.amount) + ' ' + expense.paidBy
        	self.response.write('<blockquote>%s</blockquote>' %
                                cgi.escape(expense_entry))
        	test = ExpenseEntry(expense.details, expense.amount, expense.paidBy)
        	print json.dumps(vars(test),sort_keys=True, indent=4)
            '''

app = webapp2.WSGIApplication([
    ('/', MainPage)
], debug=True)