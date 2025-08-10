from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/database.db'
app.config['SECRET_KEY'] = 'secret'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique = True)
    password = db.Column(db.String(80), nullable=False)


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw=({"placeholder": "username"}))
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw=({"placeholder": "password"}))
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError("That username already exists. Please choose another one.")

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw=({"placeholder": "username"}))
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw=({"placeholder": "password"}))
    submit = SubmitField("Login")


# landing
@app.route('/', methods = ['GET', 'POST'])
def site():
    return render_template('index.html')

# resume
@app.route('/resume', methods = ['GET', 'POST'])
def resume():
    return render_template("resume.html")

# noscam
@app.route('/noscam', methods = ['GET', 'POST'])
def noscam():
    return render_template("noscam.html")

# login
@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    return render_template("login.html", form = form)

# signup
@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template("signup.html", form = form)

if __name__ == "__main__":
    app.run(debug=True)
