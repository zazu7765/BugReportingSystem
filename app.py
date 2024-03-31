import secrets

from flask import Flask, render_template, redirect, url_for, request
from flask_login import login_user, login_required, logout_user, LoginManager, current_user
from werkzeug.security import check_password_hash

from forms import RegistrationForm, LoginForm
from models import User, db
from utilities import check_existing_employee, check_existing_user, hash_password


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
            return redirect(url_for('bugs'))
        return "hello world, we are running on " + db.engine.name + " with " + db.engine.url.__str__()

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

                return render_template("register.html", form=form, error_message= error)
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
                    return redirect(url_for('bugs'))
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
        return "asd"

    return app


app = create_app()
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run()
