import secrets

from flask import Flask, render_template, redirect, url_for, request, abort, flash
from flask_login import login_user, login_required, logout_user, LoginManager, current_user
from werkzeug.security import check_password_hash

from forms import RegistrationForm, LoginForm, SprintForm, BugReportForm, ChangePasswordForm
from models import User, db, BugReport, Sprint
from utilities import check_existing_employee, check_existing_user, hash_password, check_existing_sprint, \
    check_date_in_sprint, get_existing_user, \
    check_existing_bug_report_by_number, send_email, check_existing_email


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

    @login_manager.unauthorized_handler
    def unauthorized_callback():
        return redirect('/login?next=' + request.path)

    @app.route('/')
    def home():
        if current_user.is_authenticated:
            return render_template("home.html")
        return render_template(
            "default.html")  # "hello world, we are running on " + db.engine.name + " with " + db.engine.url.__str__()

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegistrationForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                if check_existing_user(form.username.data):
                    flash('Username already exists!', 'error')
                elif check_existing_employee(form.employee_id.data):
                    flash('Employee ID already exists!', 'error')
                elif check_existing_email(form.email.data):
                    flash('Email already exists!', 'error')
                else:
                    user = User(username=form.username.data, email=form.email.data,
                                password=hash_password(form.password.data),
                                employee_id=form.employee_id.data)
                    db.session.add(user)
                    db.session.commit()
                    return redirect(url_for('login'))

                # return render_template("register.html", form=form, error_message=error)
            else:
                for error in form.errors:
                    flash(error + ' formatting error', 'error')
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
                    if form.next.data == '' or form.next.data is None:
                        return redirect(url_for('home'))
                    return redirect(form.next.data)
                flash('Invalid username or password', 'error')
            # return render_template('login.html', form=form, error_message='Invalid username or password')

        form.next.default = request.args.get('next', '')
        form.process()
        return render_template('login.html', form=form)

    @app.route('/change_password', methods=['GET', 'POST'])
    @login_required
    def change_password():
        form = ChangePasswordForm()

        if form.validate_on_submit():
            if not check_password_hash(current_user.password, form.current_password.data):
                flash('Current password is incorrect', 'error')
            else:
                current_user.password = hash_password(form.new_password.data)
                db.session.commit()
                flash('Password changed successfully', 'success')
                return redirect(url_for('home'))

        return render_template('change_password.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('home'))

    @app.route('/bugs')
    @login_required
    def bugs():
        return render_template('bugs.html',
                               bugs=BugReport.query.all(), sprints=Sprint.query.all())

    @app.route('/bugs/<int:bug_id>')
    @login_required
    def bug(bug_id):
        bug_found = BugReport.query.filter_by(number=bug_id).first()
        if bug_found is None:
            abort(404)
        return render_template('bug.html', bug=bug_found)

    @app.route('/bug_report', methods=['GET', 'POST'])
    @login_required
    def bug_report():
        form = BugReportForm()  # Create the form obj

        if request.method == 'POST':
            print(request.date)
            if form.validate_on_submit():
                if check_existing_bug_report_by_number(form.report_number.data) is not None:
                    # Check if bug report exists
                    error = 'Bug report already exists!'
                    flash(error, 'error')
                    return redirect(url_for('bug_report'))
                else:
                    check_sprint = check_date_in_sprint(form.current_date.data)
                    if check_sprint:
                        insert_bug_report = BugReport(
                            number=form.report_number.data,
                            bug_type=form.bug_type.data,
                            description=form.bug_summary.data,
                            is_open=True,
                            is_fixed=False,
                            reason_for_close="",
                            user_id=current_user.id,
                            sprint_id=check_sprint.id
                        )
                        subscribed = bool(request.form.get('update_notification'))
                        if subscribed:  # Check if checkboxes for subscription are checked
                            current_user.subscribed_bug_reports.append(insert_bug_report)

                        db.session.add(insert_bug_report)  # Add to database
                        db.session.commit()
                        return redirect(url_for('bug_report'))  # Redirect back to the bug report page after submission
                    else:
                        flash("There is no sprint for this date yet, please create one!", 'error')
        return render_template('bug_report.html', form=form)

    @app.route('/subscribe_bug_report/<int:bug_report_id>', methods=['POST'])
    @login_required
    def subscribe_bug_report(bug_report_id):
        report = check_existing_bug_report_by_number(bug_report_id)
        if report is None:
            flash('Bug report not found', 'error')
            return redirect(url_for('bugs') + "/" + str(bug_report_id))

        user = get_existing_user(int(current_user.id))
        if user is None:
            flash('User not found', 'error')
            return redirect(url_for('bugs') + "/" + str(report.number))

        if user in report.subscribers:
            report.subscribers.remove(user)
            db.session.commit()
            flash('User unsubscribed successfully', 'success')
        else:
            report.subscribers.append(user)
            db.session.commit()
            flash('User subscribed successfully', 'success')

        return redirect(url_for('bugs') + "/" + str(report.number))

    @app.route('/edit_bug_report/<int:bug_report_id>', methods=['POST'])
    @login_required
    def edit_bug_report(bug_report_id):
        report = check_existing_bug_report_by_number(bug_report_id)
        if report is None:
            return redirect(url_for('bugs'))

        report_number = request.form.get('report_number')
        if report_number:
            report.number = report_number

        bug_type = request.form.get('bug_type')
        if bug_type:
            report.bug_type = bug_type

        description = request.form.get('description')
        if description:
            report.description = description

        db.session.commit()
        flash('Bug report updated successfully', 'success')

        return redirect(url_for('bugs') + "/" + str(bug_report_id))

    @app.route('/bug_report/close/<int:bug_report_id>', methods=['POST'])
    @login_required
    def close_bug_report(bug_report_id):
        report: BugReport = check_existing_bug_report_by_number(bug_report_id)
        if report is None:
            return redirect(url_for('bugs'))
        if report.is_open and not report.is_fixed:
            report.is_open = False
            report.reason_for_close = request.form['close_reason']
            db.session.commit()
            flash('Bug report closed successfully', 'success')
            for subscriber in report.subscribers:
                send_email(subscriber.email, f"Bug report #{bug_report_id} is closed", f"Please see the bug report and reasoning below: \n\n{report.description}\n\nReason:\n\n{report.reason_for_close}")

        else:
            flash('Bug report is already closed or marked as fixed', 'error')
        return redirect(url_for('bugs') + "/" + str(bug_report_id))

    @app.route('/bug_report/fix/<int:bug_report_id>', methods=['POST'])
    @login_required
    def fix_bug_report(bug_report_id):
        report: BugReport = check_existing_bug_report_by_number(bug_report_id)
        if not report.is_fixed and report.is_open:
            report.is_fixed = True
            db.session.commit()
            flash('Bug report marked as fixed', 'success')
            for subscriber in report.subscribers:
                send_email(subscriber.email, f"Bug report #{bug_report_id} is fixed", f"Please see the bug report below: \n\n{report.description}")
        else:
            flash('Bug report is already fixed or closed', 'error')
        return redirect(url_for('bugs') + "/" + str(bug_report_id))

    @app.route('/sprint', methods=['GET', 'POST'])
    @login_required
    def sprint():
        form = SprintForm()  # Create the form obj

        if request.method == 'POST':
            if form.validate_on_submit():
                if check_existing_sprint(form.sprint_name.data):  # Check for existing sprint
                    error = 'Sprint already exists!'
                    flash(error, 'error')
                else:
                    inserted_sprint = Sprint(start_date=form.start_date.data, end_date=form.end_date.data,
                                             # Create sprint
                                             name=form.sprint_name.data, bugs=[])
                    db.session.add(inserted_sprint)  # Add to database
                    db.session.commit()
                # Logic to process form submission
                return redirect(url_for('sprint'))  # Redirect back to the bug report page after submission
            else:
                return render_template("sprint.html", form=form, error_message=form.errors)
        # Render the bug report page and pass the form variable to the template
        # with app.app_context():
        return render_template('sprint.html', form=form)

    return app


app = create_app()
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run()
