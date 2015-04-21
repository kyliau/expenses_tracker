# processpayment.py

import datetime
import jinja2
import cgi
import os
import webapp2

from google.appengine.ext import ndb

DEFAULT_EXPENSE = 'default_expense'
DEFAULT_PERSON  = 'default_person'

def expense_key(expense_name=DEFAULT_EXPENSE):
    """ Constructs a Datastore key for Expense entity
        We use expense_name as the key
    """
    return ndb.Key('Expense', expense_name)

def person_key(person_name=DEFAULT_PERSON):
    """ Constructs a Datastore key for Person entity
        We use person_name as the key
    """
    return ndb.Key('Person', person_name)

class Expense(ndb.Model):
    """ A main model for representing an individual expense entry """
    createdDate = ndb.DateTimeProperty(auto_now_add=True)
    transactionDate = ndb.DateTimeProperty(indexed=True)
    details = ndb.StringProperty(indexed=False)
    amount = ndb.FloatProperty(indexed=False)
    paidBy = ndb.StringProperty(indexed=True)
    split = ndb.FloatProperty(repeated=True)

class Person(ndb.Model):
    """ A main model for representing a user """
    userId = ndb.IntegerProperty(indexed=False)
    name = ndb.StringProperty(indexed=True)
    shortName = ndb.StringProperty(indexed=False)

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def populatePerson():
    array = ['Edward','Hui Xian', 'Jess', 'Ji Chuan', 'Kai Boon', 'Keen Yee', 'Khai Ren', 'Lee Sin', 'Lyndy', 'Melissa', 'Paul', 'Rachel', 'Sonia', 'Tyng Yu', 'Yin Yu']
    for i in range(len(array)):
        person = Person(parent=person_key(DEFAULT_PERSON))
        person.name = array[i]
        person.shortName = array[i].replace(' ', '').lower()
        person.userId = i
        person.put()


class MainPage(webapp2.RequestHandler):
    def get(self): 
        persons_query = Person.query(
            ancestor=person_key(DEFAULT_PERSON)).order(Person.name)
        persons = persons_query.fetch()
        template = jinja_environment.get_template('template.html')
        self.response.out.write(template.render({
            'persons': persons
        }))

class ExpenseTracker(webapp2.RequestHandler):
    def post(self):
        print self.request
    
        persons_query = Person.query(
            ancestor=person_key(DEFAULT_EXPENSE)).order(Person.name)
        persons = persons_query.fetch()

        split = []
        for person in persons:
            elemId = persons.shortName + 'Amount'
            split.append(float(self.request.get(elemId, 0)))

        expense = Expense(parent=expense_key(DEFAULT_EXPENSE))
        expense.transactionDate = datetime.datetime.strptime(self.request.get('date'), "%Y-%m-%d")
        expense.details = self.request.get('details')
        expense.amount = float(self.request.get('amount', 0))
        expense.paidBy = self.request.get('paidBy')
        expense.split = split

        print expense

        expense.put()
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write("Successfully added expense!")
        #self.redirect('/admin')

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
        print message

        template = jinja_environment.get_template('admin.html')
        self.response.out.write(template.render({
            'expenses':expenses,
            'alertType':alertType,
            'message':message
        }))

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/submit', ExpenseTracker),
    ('/admin', Admin),
], debug=True)

