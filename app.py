import secrets

from flask import Flask
from flask import session
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///brs.db'
app.secret_key = secrets.token_hex()

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
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


with app.app_context():
    db.create_all()


@app.route('/')
def hello_world():
    return "hello world, we are running on "+db.engine.name+" with "+db.engine.url.__str__()


if __name__ == '__main__':
    app.run(debug=True)
