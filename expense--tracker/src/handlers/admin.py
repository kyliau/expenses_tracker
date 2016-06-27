from google.appengine.ext import ndb
from google.appengine.api import users
from src.handlers.basehandler import BaseHandler
from src.models.expense import Expense
from src.utils.jinjautil import JINJA_ENVIRONMENT
from src.utils.calculationutil import CalculationUtil as CalcUtil

class AdminHandler(BaseHandler):
    def get(self):
        projectId = self.request.get("id")
        if not projectId:
            return self.redirect("/home")
        projectKey = ndb.Key(urlsafe=projectId)
        project = projectKey.get()
        if not project:
            self.redirect("/home")
        appUser = self.appUser
        if not project.isMember(appUser):
            self.abort(401)
        members = project.getMembers()
        expenses = Expense.queryByProject(project)
        template = JINJA_ENVIRONMENT.get_template("templates/admin.html")
        template_values = {
            "current_page" : "Admin",
            "project_key"  : projectKey.urlsafe(),
            "logout_url"   : users.create_logout_url("/"),
            "members"      : members,
            "expenses"     : expenses,
            "id_resolver"  : {m.key:m for m in members},
            "is_admin"     : project.isAdmin(appUser),
            "summary" : CalcUtil.calculateSummaryForAll(members,
                                                        expenses)
        }
        self.response.write(template.render(template_values))

    # TODO: need to make this into a transaction
    def post(self):
        projectId = self.request.get("project_to_delete")
        if not projectId:
            return self.response.write("Request is invalid")
        projectKey = ndb.Key(urlsafe=projectId)
        project = projectKey.get()
        if not project:
            self.response.write("Request is invalid")
        appUser = self.appUser
        # only owner is allowed to delete project
        if appUser.key != project.owner:
            # log error message here
            return self.abort(401,
                              detail="User is not authorized to delete project")
        # TODO: Also need to delete the key from each member's profile
        # That means we need to make this a transaction
        members = project.getMembers()
        for member in members:
            member.deleteProject(project)

        # also need to delete all transactions in the project
        Expense.deleteAllExpensesInProject(project)

        ndb.put_multi(members)
        projectKey.delete()

        self.redirect("/home")