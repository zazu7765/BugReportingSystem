
# Bug Reporting System

CPS406 Software Engineering at Toronto Metropolitan University (formerly known as Ryerson University) final project.
Had two "sprints" to work on, auth was done in the first and other features in the second.

## Features

- User registration and authentication
- Bug report creation and management
- Subscription to bug reports for updates
- Closing and fixing bug reports
- Sprint management
- Statistics about bug reports in sprints

## Technologies Used

- Python
- Flask (routes)
- WTForms (form validation)
- Werkzeug (hashing)
- SQLAlchemy (database and sessions)
- Flask-Login (login session manager)
- Matplotlib (graph generation)

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/zazu7765/BugReportingSystem.git
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up the env file:
    ```text
    smtp_server = "mail.email.com"
    sender_email = "email@email.com"
    password = "password"
    port = 465
    ```
   
4. Run tests:
   ```bash
    python -m pytest
    ```
4. Run the application:

   ```bash
   python app.py
   ```

5. Access the application in your web browser at `http://localhost:5000`.

## Usage

- Register a new account or log in with an existing account.
- Create bug reports, subscribe to bug reports, and manage them accordingly.
- View statistics about bug reports in different sprints.
