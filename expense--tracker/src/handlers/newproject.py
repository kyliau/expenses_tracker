
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
        if participant is owner:
            continue    # don't send email to owner of the project
        template_values["name"]         = participant.name
        template_values["is_moderator"] = participant.key in project.moderators
        message.to   = "{} <{}>".format(participant.name, participant.email)
        message.html = template.render(template_values)
        message.send()



class CreateNewProject(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/newproject.html')
        template_values = {
            'current_page' : "Home",
            'logout_url'   : users.create_logout_url('/')
        }
        self.response.write(template.render(template_values))

    #@ndb.transactional
    def post(self):
        user = users.get_current_user()
        owner = ettypes.AppUser.queryByUserId(user.user_id())
        if not owner:
            self.abort(401)

        projectName     = self.request.get('project_name')
        numParticipants = float(self.request.get('num_participants', 0))
        participants    = self.request.get('participants')
        moderators      = self.request.get('moderators')
        numModerators   = float(self.request.get('num_moderators', 0))
        assert projectName
    
        if numParticipants > 0:
            participants = participants.split(',')
            assert len(participants) == numParticipants
        else:
            participants = []
        if numModerators > 0:
            assert numModerators <= numParticipants
            moderators = moderators.split(',')
            assert len(moderators) == numModerators
            assert all(moderator in participants for moderator in moderators)
        else:
            moderators = []
        participants.append(owner.email)
        moderators.append(owner.email)

        # need to make sure the list is unique
        participants = list(set(participants))
        moderators = list(set(moderators))

        mapper = ettypes.AppUser.mapEmailsToUsers(participants)
        participatingUsers = mapper.values()
        participantKeys = map(lambda user: user.key, participatingUsers)
        moderatorKeys = map(lambda moderator: mapper[moderator].key, moderators)
        newProject = ettypes.Project.addNewProject(projectName,
                                                   owner.key,
                                                   participantKeys,
                                                   moderatorKeys)
        assert newProject

        for participant in participatingUsers:
            participant.addProject(newProject)
        ndb.put_multi(participatingUsers)

        notifyAllParticipants = self.request.get('notify_all_participants')
        if notifyAllParticipants:
            sendNewProjectEmail(newProject, owner, participatingUsers)
        #settings = ettypes.Settings.createNewSettings(newProject, participatingUsers)
        #ndb.put_multi(settings)
        query_params = {
            'id' : newProject.key.urlsafe()
        }
        self.redirect('project?' + urllib.urlencode(query_params))