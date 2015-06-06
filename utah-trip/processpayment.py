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
    individualAmount = ndb.FloatProperty(repeated=True)

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
    array = ['Edward','Hui Xian', 'Jess', 'Ji Chuan', 'Kai Boon', 'Keen Yee',
             'Khai Ren', 'Lee Sin', 'Lyndy', 'Melissa', 'Paul', 'Sonia',
             'Tyng Yu', 'Yin Yu']
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
        persons_query = Person.query(
            ancestor=person_key(DEFAULT_PERSON)).order(Person.name)
        persons = persons_query.fetch()

        expense = Expense(parent=expense_key(DEFAULT_EXPENSE))
        expense.transactionDate = datetime.datetime.strptime(self.request.get('date'), "%Y-%m-%d")
        expense.details = self.request.get('details')
        expense.amount = float(self.request.get('amount', 0))
        expense.paidBy = self.request.get('paidBy')
        for person in persons:
            elemId = person.shortName + 'Amount'
            individualAmount = self.request.get(elemId, 0) or 0
            expense.individualAmount.append(float(individualAmount))
        if abs(sum(expense.individualAmount) - expense.amount) < 0.05:
            expense.put()
            self.redirect('/summary?user=%s' % expense.paidBy)
        else:
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.write("Amount does not tally. Transaction is not recorded")

class Summary(webapp2.RequestHandler):
    def get(self):

        persons_query = Person.query(
            ancestor=person_key(DEFAULT_PERSON)).order(Person.name)
        persons = persons_query.fetch()
        
        # create a map of person name to id
        nameToId = {}
        for p in persons:
            nameToId[p.name] = p.userId

        # a positive amount here means the user spent more than paid
        amount = [0] * len(persons)

        expenses_query = Expense.query(ancestor=expense_key(DEFAULT_EXPENSE)).order(-Expense.transactionDate, -Expense.createdDate)
        expenses = expenses_query.fetch()

        for expense in expenses:
            uid = nameToId[expense.paidBy]
            amount[uid] -= expense.amount
            assert len(expense.individualAmount) == len(amount)
            amount = [a + b for (a, b) in zip(expense.individualAmount,
                                              amount)]

        user = self.request.get('user')
        person_query = Person.query(Person.name == user)
        person = person_query.fetch()
        if not person:
            template = jinja_environment.get_template('summary.html')
            self.response.out.write(template.render({
                'amount' : amount,
                'persons': persons,
                'user': None
            }))
            return

        user = person[0]
        expenses_query = Expense.query(
            ancestor=expense_key(DEFAULT_EXPENSE)).order(-Expense.transactionDate, -Expense.createdDate)
        expenses = expenses_query.fetch()

        totalPaid = 0
        totalSpent = 0
        userExpenses = []
        for expense in expenses:
            addToArray = False
            if expense.paidBy == user.name:
                totalPaid += expense.amount
                addToArray = True
            if expense.individualAmount[user.userId] > 0:
                totalSpent += expense.individualAmount[user.userId]
                addToArray = True
            if addToArray:
                userExpenses.append(expense)

        amountOwed = totalSpent - totalPaid
        
        message = ''
        alertType = 'alert-info'
        if abs(amountOwed) < 0.05:
            message = 'All dues are clear'
            alertType = 'alert-success'
        elif amountOwed > 0:
            message = '%s owes Auntie Terry $%s' % (user.name, "{:.2f}".format(amountOwed))
        else:
            message = 'Auntie Terry owes %s $%s' % (user.name, "{:.2f}".format(abs(amountOwed)))

        template = jinja_environment.get_template('summary.html')
        self.response.out.write(template.render({
            'persons': persons,
            'user': user,
            'expenses': userExpenses,
            'alertType': alertType,
            'message': message,
            'totalPaid': totalPaid,
            'totalSpent': totalSpent
        }))

class Admin(webapp2.RequestHandler):
    def get(self):
        expenses_query = Expense.query(
            ancestor=expense_key(DEFAULT_EXPENSE)).order(-Expense.transactionDate, -Expense.createdDate)
        expenses = expenses_query.fetch()

        persons_query = Person.query(
            ancestor=person_key(DEFAULT_PERSON)).order(Person.name)
        persons = persons_query.fetch()

        template = jinja_environment.get_template('admin.html')
        self.response.out.write(template.render({
            'expenses': expenses,
            'persons': persons
        }))

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/submit', ExpenseTracker),
    ('/admin', Admin),
    ('/summary', Summary),
], debug=True)

