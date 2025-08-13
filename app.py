from flask import Flask, render_template, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sr_online.db?check_same_thread=False'
app.config['SECRET_KEY'] = 'secret'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique = True)
    password = db.Column(db.String(80), nullable=False)


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
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
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                return redirect(url_for('login_fail'))
        else:
            return redirect(url_for('login_fail'))
    else:
        return render_template("login.html", form = form)

@app.route('/dashboard', methods = ['GET', 'POST'])
@login_required
def dashboard():
    if current_user.is_authenticated:
        username = current_user.username
        return render_template('dashboard.html', username = username)
    else:
        return "User is not authenticated"

#logout
@app.route('/logout', methods=('GET', 'POST'))
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# signup
@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            return redirect(url_for("signup_fail"))
        else:
            hashed_password = bcrypt.generate_password_hash(form.password.data)
            new_user = User(username=form.username.data, password=hashed_password)

            db.session.add(new_user)
            db.session.commit()

        return redirect(url_for('login'))
    return render_template("signup.html", form = form)

# if user fails sign in or login
@app.route('/login_fail')
def login_fail():
        flash('Invalid username/password, please try again.', 'error')
        return redirect(url_for("login"))

@app.route('/signup_fail')
def signup_fail():
        flash('Username is already taken, please choose another one.', 'error')
        return redirect(url_for("signup"))



if __name__ == "__main__":
    app.run(debug=True)
