### Tracker
- users [User[]]
- projects [Project[]]

### User
- user_id (from Google Account) [string]
- date_created [timestamp]
- name [string]
- last_login [timestamp]
- preference [Preference]
- email [string]

### Project
- name [string]
- url [string]
- owner_id [string]
- participants [string[]]
- date_created [timestamp]
- entries [Expense[]]

### Expense (Entry)
- time_created [timestamp]
- transaction_date [date]
- description [string]
- amount [double]
- paid_by [User]
- shared_by [JSON]

### Preference
- get_notified_all [Boolean]
- get_notified_relevant [Boolean]

#### Links
1. [Users Python API Overview] (https://cloud.google.com/appengine/docs/python/users/)
