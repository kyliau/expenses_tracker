from google.appengine.api import mail
from src.utils.jinjautil import JINJA_ENVIRONMENT

class EmailUtil:
    """Namespace for functions that handles email"""

    @staticmethod
    def sendNewProjectEmail(project, owner, participants):
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

        for participant in participants:
            #if participant is owner:
            #    continue    # don't send email to owner of the project
            template_values["name"]         = participant.name
            template_values["is_moderator"] = participant.key in project.moderators
            message.to   = "{} <{}>".format(participant.name, participant.email)
            message.html = template.render(template_values)
            message.send()

    @staticmethod
    def sendEmail(project, expense):
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

        # we need to build a map of userKey to the amount of the user
        def buildMap(result, indvAmt):
            result[indvAmt.user] = indvAmt.amount
            return result
        userKeyToAmountMap = reduce(buildMap, expense.individual_amount, {})

        usersInvolved = []
        # build the message body
        for participant in project.getAllParticipants():
            assert project.key in participant.projects

            emailOption = participant.getSettingsForProject(project).receive_email
            assert emailOption in ["all", "relevant", "none"]

            amount = userKeyToAmountMap[participant.key]
            assert amount >= 0
            if amount > 0:
                template_values["splits"].append({
                    "name"   : participant.name,
                    "amount" : amount
                })
            isPayer = (expense.paid_by == participant.key)
            if (emailOption == "all" or
            (emailOption == "relevant" and (isPayer or amount > 0))):
                usersInvolved.append(participant)

        template = JINJA_ENVIRONMENT.get_template("templates/newTransactionEmail.html")
        message.body = template.render(template_values)
        for user in usersInvolved:
            message.to = "{} <{}>".format(user.name, user.email)
            #message.html = "<pre>{}</pre>".format(body)
            message.send()

