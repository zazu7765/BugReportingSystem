from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    employee_id = StringField('Employee ID', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class BugReportForm(FlaskForm):
    report_number = StringField('Report Number', validators=[DataRequired()])
    bug_type = StringField('Bug Type', validators=[DataRequired()])
    bug_summary = StringField('Bug Summary', validators=[DataRequired()])
    progress_notification = BooleanField('Notify me about progress')
    update_notification = BooleanField('Notify me about updates')
    submit = SubmitField('Submit Report')
    
class SprintForm(FlaskForm):
    sprint_name = StringField('Sprint Name', validators=[DataRequired()])
    start_date = StringField('Start Date', validators=[DataRequired()])
    end_date = StringField('End Date', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    progress_notification = BooleanField('Notify me about sprint progress')
    update_notification = BooleanField('Notify me about sprint updates')
    submit = SubmitField('Create Sprint')
