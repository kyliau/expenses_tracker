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
    for appUser in usersInvolved:
            message.to = "{} <{}>".format(participant.name, participant.email)
            #message.html = "<pre>{}</pre>".format(body)
            message.send()



class ProjectHome(webapp2.RequestHandler):
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
        user = users.get_current_user()
        appUser = ettypes.AppUser.queryByUserId(user.user_id())
        if not appUser or appUser.key not in project.participants:
            self.abort(401)
        template = JINJA_ENVIRONMENT.get_template('templates/project.html')
        template_values = {
            'current_page' : "Home",
            'project'      : project,
            'logout_url'   : users.create_logout_url('/'),
            'participants' : project.getAllParticipants(),
            'current_user' : appUser
        }
        self.response.write(template.render(template_values))

    def post(self):
        encodedKey   = self.request.get('project_key')
        date         = self.request.get('date')
        amount       = float(self.request.get('amount', 0) or 0)
        details      = self.request.get('details')
        paidBy       = self.request.get('paid_by')
        splitAll     = self.request.get('split_all')
        splitEqually = self.request.get('split_equally')
        splitWith    = self.request.get('split_with')

        #TODO data validation!
        assert amount > 0

        projectKey = ndb.Key(urlsafe=encodedKey)
        project = projectKey.get()
        assert project

        paidByKey = ndb.Key(urlsafe=paidBy)
        assert paidByKey in project.participants

        transactionDate = datetime.strptime(date, "%Y-%m-%d")

        # TODO: abstract this out in the model instead..
        expense = ettypes.Expense(parent=projectKey,
                                  paid_by=paidByKey,
                                  transaction_date=transactionDate,
                                  details=details,
                                  amount=amount,
                                  split_equally=(splitEqually=="on"))
        totalAmount = 0
        for participant in project.participants:
            amt = float(self.request.get(participant.urlsafe(), 0) or 0)
            assert amt >= 0
            totalAmount += amt
            indvAmt = ettypes.IndividualAmount(user=participant, amount=amt)
            expense.individual_amount.append(indvAmt)
        assert abs(totalAmount - amount) < 0.01
        expense.put()
        # check if we need to send the email
        sendEmail(project, expense)
        self.redirect('/summary?id=' + project.key.urlsafe())