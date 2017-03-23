#from google.appengine.api import mail
from src.models.projectsettings import ProjectSettings
from src.utils.jinjautil import JINJA_ENVIRONMENT
from src.utils.configutil import ConfigUtil
import sendgrid
from sendgrid.helpers.mail import Email, Content, Mail

SENDGRID_API_KEY = ConfigUtil.get("SendGridApiKey")
SG = sendgrid.SendGridAPIClient(apikey=SENDGRID_API_KEY)
SENDER = Email(email="admin@expense--tracker.appspotmail.com",
               name="Expense Tracker")

def calculateSplit(members, individualAmount):
    """
    Return a list of user name and user amount if user amount is
    more than zero.
    """
    splits = []
    for member in members:
        amount = individualAmount[member.key]
        assert amount >= 0
        if amount > 0:
            splits.append({
                "name"   : member.name,
                "amount" : amount
            })

    maxLen = max([len(s["name"]) for s in splits])
    for s in splits:
        s["name"] = s["name"] + " "*(maxLen - len(s["name"]))

    return splits

def determineRecipients(project, members, individualAmount, payer):
    """
    Return a subset of the specified 'members' that should receive
    a notification email about a transaction. Conditions to determine
    whether a user receives an email are:
    1. User amount is more than zero
    2. User is the payer for the transaction
    3. User settings is set to receive notifications
    """
    recipients = []
    for member in members:
        settings    = ProjectSettings.getUserSettingsForProject(member, project)
        isPayer     = (payer.key == member.key)
        amount      = individualAmount[member.key]
        isInvolved  = (isPayer or amount > 0)
        emailChoice = settings.receive_email
        isRelevant  = (emailChoice == "relevant" and isInvolved)
        if emailChoice == "all" or isRelevant:
            recipients.append(member)
    return recipients

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
        subject = "[Expense Tracker] {} added you to project {}!".format(
            owner.name,
            project.name
        )
        template_location = "templates/newProjectEmail.html"
        template = JINJA_ENVIRONMENT.get_template(template_location)
        for member in members:
            #if participant is owner:
            #    continue    # don't send email to owner of the project
            template_values["name"]     = member["name"]
            template_values["is_admin"] = member["isAdmin"]
            to_email = Email(email=member["email"], name=member["name"])
            content = Content(type="text/html",
                              value=template.render(template_values))
            mail = Mail(SENDER, subject, to_email, content)
            SG.client.mail.send.post(request_body=mail.get())

    @staticmethod
    def sendNewTransactionEmail(project, expense):
        """
        Send an email to all relevant members in the specified 'project'
        for the specified 'expense'.
        """
        payer = expense.paid_by.get()
        individualAmount = {ia.user_key:ia.amount for
                            ia in expense.individual_amount}
        members = project.getMembers()
        template_values = {
            "project_name" : project.name,
            "payer"        : payer.name,
            "expense"      : {
                "transaction_date" : expense.transaction_date,
                "amount"           : expense.amount,
                "details"          : expense.details
            },
            "splits" : calculateSplit(members, individualAmount)
        }

        template_location = "templates/newTransactionEmail.html"
        template = JINJA_ENVIRONMENT.get_template(template_location)

        subject = "[{}] {} paid ${:.2f} for {}".format(project.name,
                                                       payer.name,
                                                       expense.amount,
                                                       expense.details)
        content = Content(type="text/html",
                          value=template.render(template_values))

        recipients = determineRecipients(project,
                                         members,
                                         individualAmount,
                                         payer)
        for recipient in recipients:
            to_email = Email(email=recipient.email,
                             name=recipient.name)
            mail = Mail(SENDER, subject, to_email, content)
            try:
                response = SG.client.mail.send.post(request_body=mail.get())
            except:
                pass
            #print(response.status_code)
            #print(response.body)
            #print(response.headers)

