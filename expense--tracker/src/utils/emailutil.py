from google.appengine.api import mail
from src.models.projectsettings import ProjectSettings
from src.utils.jinjautil import JINJA_ENVIRONMENT

class EmailUtil(object):
    """Namespace for functions that handles email"""

    @staticmethod
    def sendNewProjectEmail(project, owner, members):
        """
        Send a notification email to the specified 'members' of the
        new 'project' created by 'owner'.
        """

        template_values = {
            "owner"        : owner.name,
            "project_name" : project.name,
            "project_id"   : project.key.urlsafe()
        }
        message = mail.EmailMessage()
        message.sender = "Expense Tracker <admin@expense--tracker.appspotmail.com>"
        subject = "[Expense Tracker] {} added you to project {}!"
        message.subject = subject.format(owner.name, project.name)
        template = JINJA_ENVIRONMENT.get_template('templates/newProjectEmail.html')

        for member in members:
            #if participant is owner:
            #    continue    # don't send email to owner of the project
            template_values["name"]     = member["name"]
            template_values["is_admin"] = member["isAdmin"]
            message.to = "{} <{}>".format(member["name"],
                                          member["email"])
            message.html = template.render(template_values)
            message.send()

    @staticmethod
    def sendNewTransactionEmail(project, expense):
        paidBy = expense.paid_by.get()
        message = mail.EmailMessage()
        message.sender = "Expense Tracker <admin@expense--tracker.appspotmail.com>"
        subject = "[{}] {} paid ${:.2f} for {}"
        message.subject = subject.format(project.name,
                                         paidBy.name,
                                         expense.amount,
                                         expense.details)
        template_values = {
            'project_name' : project.name,
            'payer'        : paidBy.name,
            'expense'      : {
                'transaction_date' : expense.transaction_date,
                'amount'           : expense.amount,
                'details'          : expense.details
            },
            'splits' : []
        }

        individualAmount = {ia.user_key:ia.amount for 
                            ia in expense.individual_amount}
        receipients = []
        # build the message body
        for member in project.getMembers():
            assert project.key in member.projects
            settings = ProjectSettings.getSettingsByFilter(member,
                                                           project)
            emailOption = settings.receive_email
            assert emailOption in ["all", "relevant", "none"]
            amount = individualAmount[member.key]
            assert amount >= 0
            if amount > 0:
                template_values["splits"].append({
                    "name"   : member.name,
                    "amount" : amount
                })
            isPayer = (expense.paid_by == member.key)
            isInvolved = (isPayer or amount > 0)
            isRelevant = (emailOption == "relevant" and isInvolved)
            if emailOption == "all" or isRelevant:
                receipients.append(member)

        templateLocation = "templates/newTransactionEmail.html"
        template = JINJA_ENVIRONMENT.get_template(templateLocation)
        message.body = template.render(template_values)
        for user in receipients:
            message.to = "{} <{}>".format(user.name, user.email)
            #message.html = "<pre>{}</pre>".format(body)
            message.send()

