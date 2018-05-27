import sqlite3
import sqlite3 as lite
import os
from flask import Flask, render_template, request
from sightengine.client import SightengineClient
import flask
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = flask.Flask(__name__,static_folder='static')
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    avatar = db.Column(db.String(500), unique=True)


class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')


class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


def EmailDaSuDung(emailuser):
    import sqlite3
    db = sqlite3.connect('database.db')
    cur = db.cursor()
    cur.execute('SELECT email FROM user')
    email = cur.fetchall()
    for i in email:
        if i == emailuser:
            return True
    return False


def CheckId(user):
    import sqlite3
    db = sqlite3.connect('database.db')
    cur = db.cursor()
    cur.execute('SELECT * FROM user')
    email = cur.fetchall()

# tạo ra folder lưu ảnh
UPLOAD_FOLDER = os.path.basename('uploads')
app.config['uploads_FOLDER'] = UPLOAD_FOLDER


@app.route('/avatarupdate')
def AvatarUpdate():
    return render_template('avatarUpdate.html')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['image']
    filename = os.path.join(app.config['uploads_FOLDER'], file.filename)
    file.save(filename)
    db = sqlite3.connect('database.db')
    cur = db.cursor()
    #cần lấy id ra và update
    print(filename)
    cur.execute('UPDATE user SET avatar = filename WHERE id = id')
    return render_template('homeChat.html', init=True)


@app.route('/')
def hello():
    return flask.render_template("home.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return render_template('homeChat.html')

        # return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'
    return flask.render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        if EmailDaSuDung(form.email.data):
            return flask.render_template('singupfalse.html')
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        avatar_none = "https://hinhnendep.pro/wp-content/uploads/2015/12/hinh-anh-nguoi-go-dan-bo-buon-11.jpg"
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password,
                        avatar=avatar_none)
        db.session.add(new_user)
        db.session.commit()
        return flask.render_template('avatarUpdate.html')
        # return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'
    return flask.render_template('signup.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return flask.redirect(flask.url_for('homeChat.html'))


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True)
