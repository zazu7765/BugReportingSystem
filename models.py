from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    employee_id = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'


class BugReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer(), unique=True, nullable=False)
    bug_type = db.Column(db.String(), nullable=False)
    description = db.Column(db.Text, nullable=False)
    subscribed = db.Column(db.Boolean(), default=False)
    is_open = db.Column(db.Boolean(), default=True)
    is_fixed = db.Column(db.Boolean(), default=False)
    reason_for_close = db.Column(db.String())

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<BugReport {self.report_number}>'
