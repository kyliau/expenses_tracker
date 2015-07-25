Expense Tracker
===============

1. Homepage
 - Explain the features of the site
 - Inform user that sign-in with Google Account is required
2. User homepage
 - Show a list of 'projects' the user has created
 - Show a list of 'projects' the user is involved in
 - Allow the user to create a new project
3. Project homepage
 - Restricted to project owner and participants only [optional]
 - Show a summary table for the project
 - Show a drop-down menu allowing the user to see personalized expenses
 - Show a link to all entries for the project
 - If owner
    - Allow owner to rename project
    - Allow owner to project
    - Allow owner to add participants
    - Allow owner to add / delete moderators
    - Allow owner to delete participants
      - quite tricky if there are existing entries involving the user to be deleted
 - Preference
   - Allows the user to set whether to receive email notification
      - For all entries, or
      - Only entries related to the user
4. Show all entries
 - If owner
    - Allow owner to modify amount, description, etc
    - Allow owner to delete an entry
   
Misc
----
- Each project has exactly one owner
