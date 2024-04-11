from werkzeug.security import generate_password_hash

from models import User, BugReport, Sprint


def check_existing_employee(employee_id):
    existing_employee = User.query.filter_by(employee_id=employee_id).first()
    return existing_employee


def check_existing_user(username):
    existing_user = User.query.filter_by(username=username).first()
    return existing_user

def check_existing_bug_report(number):
    existing_bug_report = BugReport.query.filter_by(number=number).first()
    return existing_bug_report

def check_open_bug_report(number):
    existing_open_report = BugReport.query.filter_by(number=number).is_open
    return existing_open_report

def check_fixed_bug_report(number):
    fixed_bug_report = BugReport.query.filter_by(number=number).is_fixed
    return fixed_bug_report

def check_existing_sprint(sprint_name):
    existing_sprint = Sprint.query.filter_by(sprint_name).first()
    return existing_sprint

def hash_password(password):
    return generate_password_hash(password, method='pbkdf2')
