from models import User


def check_existing_employee(employee_id):
    existing_employee = User.query.filter_by(employee_id=employee_id).first()
    return existing_employee


def check_existing_user(username):
    existing_user = User.query.filter_by(username=username).first()
    return existing_user
