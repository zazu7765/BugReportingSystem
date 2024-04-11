import secrets

from flask import Flask, render_template, redirect, url_for, request, abort
from flask_login import login_user, login_required, logout_user, LoginManager, current_user
from sqlalchemy import desc
from werkzeug.security import check_password_hash

from forms import RegistrationForm, LoginForm, SprintForm, BugReportForm
from models import User, db, BugReport, Sprint
from utilities import check_existing_employee, check_existing_user, hash_password, check_existing_bug_report, check_fixed_bug_report, check_open_bug_report, check_existing_sprint


def create_app(testing=False):
    app = Flask(__name__)
    if testing:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///brs.db'
    app.secret_key = secrets.token_hex()
    db.init_app(app)
    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/')
    def home():
        if current_user.is_authenticated:
            return render_template("home.html")
        return render_template("default.html")#"hello world, we are running on " + db.engine.name + " with " + db.engine.url.__str__()

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegistrationForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                if check_existing_user(form.username.data):
                    error = 'Username already exists!'
                elif check_existing_employee(form.employee_id.data):
                    error = 'Employee ID already exists!'
                else:
                    user = User(username=form.username.data, email=form.email.data,
                                password=hash_password(form.password.data),
                                employee_id=form.employee_id.data)
                    db.session.add(user)
                    db.session.commit()
                    return redirect(url_for('login'))

                return render_template("register.html", form=form, error_message=error)
            else:
                return render_template("register.html", form=form, error_message=form.errors)
        return render_template('register.html', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                user = check_existing_user(form.username.data)
                if user and check_password_hash(user.password, form.password.data):
                    login_user(user)
                    return redirect(url_for('home'))
                return render_template('login.html', form=form, error_message='Invalid username or password')
        return render_template('login.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('home'))

    @app.route('/success')
    def success():
        return "Successful registration!"

    @app.route('/bugs')
    @login_required
    def bugs():
        return render_template('bugs.html',
                               bugs=BugReport.query.all())
    
    @app.route('/bug_report', methods=['GET', 'POST'])
    @login_required
    def bug_report():
        form = BugReportForm()  # Create the form obj

        if request.method == 'POST':
            if form.validate_on_submit():
                if check_existing_bug_report(form.report_number.data): # Check if bug report exists
                    error = 'Bug report already exists!' 
                    if not check_open_bug_report(form.report_number.data): # Check is bug report is open
                        error = 'Bug report is not open!'
                    elif check_fixed_bug_report(form.report_number.data): # Check if bug report is fixed
                        error = 'Bug report is fixed!'
                else:
                    if request.form.get('progress_notification') or request.form.get('update_notification'): # Check if checkboxes for subscription are checked
                        bug_report = BugReport(number=form.report_number.data, bug_type=form.bug_type.data, # Create bug report accordingly
                        description=form.bug_summary.data, subscribed=True, is_open=True, is_fixed=False,
                        reason_for_close="", user_id=current_user.id, sprint_id=1)
                    else:
                        bug_report = BugReport(number=form.report_number.data, bug_type=form.bug_type.data, 
                        description=form.bug_summary.data, subscribed=False, is_open=True, is_fixed=False,
                        reason_for_close="", user_id=current_user.id, sprint_id=1)
                    db.session.add(bug_report) # Add to database
                    db.session.commit()
                    # Logic to process form submission
                    return redirect(url_for('bug_report'))  # Redirect back to the bug report page after submission
        # Should return render templates here for errors...

        # Render the bug report page and pass the form variable to the template
        #with app.app_context():
        return render_template('bug_report.html', form=form)
    
    @app.route('/sprint', methods=['GET', 'POST'])
    @login_required
    def sprint():
        form = SprintForm()  # Create the form obj

        if request.method == 'POST':
            if form.validate_on_submit():
                if check_existing_sprint(form.sprint_name.data): # Check for existing sprint
                    error = 'Sprint already exists!'
                else:
                    sprint = Sprint(start_date=form.start_date.data, end_date=form.end_date.data, # Create sprint
                                    name=form.sprint_name.data, bugs=[])
                    db.session.add(sprint) # Add to database
                    db.session.commit()
                # Logic to process form submission
                return redirect(url_for('sprint'))  # Redirect back to the bug report page after submission
            else:
                return render_template("sprint.html", form=form, error_message=form.errors)
        # Render the bug report page and pass the form variable to the template
        #with app.app_context():
        return render_template('sprint.html', form=form)
    
    @app.route('/bugs/<int:bug_id>')
    @login_required
    def bug(bug_id):
        bug_found = BugReport.query.filter_by(id=bug_id).first()
        if bug_found is None:
            abort(404)
        return render_template('bug.html', bug=bug_found)

    return app


app = create_app()
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run()
