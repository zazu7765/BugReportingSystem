import secrets

from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

from forms import RegistrationForm
from models import User, db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///brs.db'
app.secret_key = secrets.token_hex()

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return "hello world, we are running on " + db.engine.name + " with " + db.engine.url.__str__()


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            existing_user = User.query.filter_by(username=form.username.data).first()
            if existing_user:
                return render_template("register.html", form=form, error_message="Username already exists")

            existing_employee = User.query.filter_by(employee_id=form.employee_id.data).first()
            if existing_employee:
                return render_template("register.html", form=form, error_message="Employee already exists")
            user = User(username=form.username.data, email=form.email.data,
                        password=generate_password_hash(form.password.data),
                        employee_id=form.employee_id.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('success'))
        else:
            return render_template("register.html", form=form, error_message = form.errors)
    return render_template('register.html', form=form)



@app.route('/success')
def success():
    return "Successful registration!"


if __name__ == '__main__':
    app.run(debug=True)
