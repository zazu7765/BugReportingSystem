import os, smtplib, ssl, dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from werkzeug.security import generate_password_hash
from models import User, BugReport, Sprint

if not dotenv.load_dotenv():
    print('..env file missing, please add it to root file directory')


def check_existing_employee(employee_id):
    existing_employee = User.query.filter_by(employee_id=employee_id).first()
    return existing_employee


def get_existing_user(user_id):
    return User.query.get(user_id)


def check_existing_user(username):
    existing_user = User.query.filter_by(username=username).first()
    return existing_user


def check_existing_email(email):
    return User.query.filter_by(email=email).first()


def check_existing_bug_report_by_number(number):
    return BugReport.query.filter_by(number=number).first()


def check_existing_sprint(sprint_name):
    existing_sprint = Sprint.query.filter_by(name=sprint_name).first()
    return existing_sprint


def check_date_in_sprint(date):
    existing_sprint = Sprint.query.filter(Sprint.start_date <= date, Sprint.end_date >= date).first()
    return existing_sprint


def hash_password(password):
    return generate_password_hash(password, method='pbkdf2')


def send_email(receiver_email, subject, body, smtp_server=None, sender_email=None, password=None):
    port = os.getenv('port') or 465
    smtp_server = smtp_server or os.getenv("smtp_server")
    sender_email = sender_email or os.getenv("sender_email")
    password = password or os.getenv("password")

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            if hasattr(server, 'login'):
                server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print(f"\nEmail Sent Successfully to {receiver_email}")
        return 1
    except Exception as error:
        print("Sending email failed due to:")
        print(error)
        return 0


if __name__ == "__main__":
    send_email("test@test.com", "test", "this is a test, fear not citizen")
