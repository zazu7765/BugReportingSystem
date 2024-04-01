from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(db.Model, UserMixin):
    id: db.Column = db.Column(db.Integer, primary_key=True)
    username: db.Column = db.Column(db.String(), unique=True, nullable=False)
    employee_id: db.Column = db.Column(db.String(), unique=True, nullable=False)
    password: db.Column = db.Column(db.String(), nullable=False)
    email: db.Column = db.Column(db.String(), unique=True, nullable=False)

    def __init__(self, username: str, employee_id: str, password: str, email: str):
        self.username = username
        self.email = email
        self.employee_id = employee_id
        self.password = password
    def __repr__(self):
        return f'<User {self.username}>'


class Sprint(db.Model):
    id: db.Column = db.Column(db.Integer, primary_key=True)
    start_date: db.Column = db.Column(db.DateTime, nullable=False)
    end_date: db.Column = db.Column(db.DateTime, nullable=False)
    name: db.Column = db.Column(db.String(), nullable=False)
    bugs = db.relationship('BugReport', backref='sprint', lazy=True)


class BugReport(db.Model):
    id: db.Column = db.Column(db.Integer, primary_key=True)
    number: db.Column = db.Column(db.Integer(), unique=True, nullable=False)
    bug_type: db.Column = db.Column(db.String(), nullable=False)
    description: db.Column = db.Column(db.Text, nullable=False)
    subscribed: db.Column = db.Column(db.Boolean(), default=False)
    is_open: db.Column = db.Column(db.Boolean(), default=True)
    is_fixed: db.Column = db.Column(db.Boolean(), default=False)
    reason_for_close: db.Column = db.Column(db.String())
    created = db.Column(db.String(), default=datetime.utcnow, nullable=False)
    archived_at = db.Column(db.DateTime, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sprint_id = db.Column(db.Integer, db.ForeignKey('sprint.id'), nullable=False)

    def __repr__(self):
        return f'<BugReport {self.report_number}>'
