from flask import Flask, render_template, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError, Email
from flask_bcrypt import Bcrypt
from datetime import datetime
import sqlite3

# please create config file please
from config import SECRET_KEY

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sr_online.db?check_same_thread=False'
app.config['SECRET_KEY'] = 'SECRET_KEY'
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
    mc = db.Column(db.String(80), nullable =False, unique = True)

class UserCharacter(db.Model, UserMixin):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    character_id = db.Column(db.Integer, primary_key = True, unique = True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable = False)
    character_number = db.Column(db.Integer)
    name = db.Column(db.String(40), nullable=False)
    race = db.Column(db.String(20), nullable=False)
    hero_class = db.Column(db.String(20), nullable = False)
    background = db.Column(db.String(80), nullable = False)
    alignment = db.Column(db.String(20), nullable = False)
    proficiencies = db.Column(db.String(80), nullable = False)
    equipment = db.Column(db.String(220), nullable = False)
    backstory = db.Column(db.String(220), nullable = True)


    __table_args__ = (
            db.UniqueConstraint('user_id', 'character_number', name='uq_user_character_number'),
        )



class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    mc = StringField(validators= [InputRequired(),Length(min=4, max=40)], render_kw={"placeholder": "Minecraft Name"})
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")

class CharacterCreator(FlaskForm):
    name = StringField(validators=[InputRequired(), Length(min=1, max=40)], render_kw={"placeholder": "Name"})
    race = StringField(validators=[InputRequired(), Length(min=1, max=20)], render_kw={"placeholder": "Race"})
    hero_class = StringField(validators=[InputRequired(), Length(min=1, max=20)], render_kw={"placeholder": "Class"})
    background = StringField(validators=[InputRequired(), Length(min=1, max=20)], render_kw={"placeholder": "Background"})
    alignment = StringField(validators=[InputRequired(), Length(min=1, max=20)], render_kw={"placeholder": "Alignment"})
    proficiencies = StringField(validators=[InputRequired(), Length(min=1, max=80)], render_kw={"placeholder": "Proficiencies"})
    equipment = StringField(validators=[InputRequired(), Length(min=1, max=220)], render_kw={"placeholder": "Equipment"})
    backstory = StringField(validators=[Length(min=1, max=220)], render_kw={"placeholder": "Backstory"})
    submit = SubmitField("Create Character")

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
    username = current_user.username
    mc = current_user.mc
    return render_template('dashboard.html', username = username, mc = mc)

@app.route('/dashboard/character', methods = ['GET', 'POST'])
@login_required
def character():
    form = CharacterCreator()
    username = current_user.username
    id = current_user.id
    mc = current_user.mc
    character = UserCharacter.query.filter_by(user_id=id)
    
    if character:
        # fetching user_character from Databse
        conn = sqlite3.connect('instance/sr_online.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT character_id,name, race, hero_class, background, alignment, proficiencies, equipment, backstory FROM user_character WHERE user_id = {id}")
        data = cursor.fetchall()
        conn.close()
    else:
        data = "False"


    if form.validate_on_submit():
        new_character = UserCharacter(user_id = id, name=form.name.data, race=form.race.data, hero_class=form.hero_class.data, background=form.background.data, alignment=form.alignment.data, proficiencies=form.proficiencies.data, equipment=form.equipment.data, backstory=form.backstory.data,)
        db.session.add(new_character)
        db.session.commit()
        return redirect(url_for('character'))


    return render_template('character.html', username = username, mc=mc, form=form, data = data)

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
            new_user = User(username=form.username.data, password=hashed_password, mc=form.mc.data)

            db.session.add(new_user)
            db.session.commit()

        return redirect(url_for('login'))
    return render_template("signup.html", form = form)

# if user fails sign up or login
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
