from flask import Flask, render_template, send_file, session, request, redirect
from werkzeug import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, roles_required
from flask_security.utils import encrypt_password
import os, time
from src.json_parser import parse_json, post
# TODO Remove random
from random import randint

# Create app
app = Flask(__name__)
app.config['DEBUG'] = True

app.config['SECRET_KEY'] = 'n0b0dy-c0u1d-gue55-th15'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# the salt is a workaround for a bug, as flask-security salts tfrom flask_security.utils import encrypt_password, verify_password, get_hmache passwords automatically
# but somehow it doesn't notice it.
app.config['SECURITY_PASSWORD_SALT'] = os.urandom(1)
app.config['SECURITY_TRACKABLE'] = True

app.config['UPLOAD_FOLDER'] = 'config'
# max upload size is 50 KB
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024
ALLOWED_EXTENSIONS = set(['cfg'])

# Create database connection object
db = SQLAlchemy(app)

# Define models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(100))
    current_login_ip = db.Column(db.String(100))
    login_count = db.Column(db.Integer())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

class Config(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    miner_number = db.Column(db.Integer(), primary_key=True)

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

def get_curr_user():
    return User.query.filter_by(id=session["user_id"]).first().email

# Create a user to test withflask_security.utils
@app.before_first_request
def create_user():
    db.create_all()
    user_datastore.create_role(name='admin')
    user_datastore.create_user(email='user@email.com', password=encrypt_password('password'), roles=['admin'])
    user_datastore.create_user(email='fake@email.com', password=encrypt_password('password1'))
    user_datastore.create_user(email='pseudo@email.com', password=encrypt_password('password2'))
    db.session.commit()

# Views
@app.route('/')
@login_required
def index():
    return render_template('index.html', container=get_mock_container(), data=parse_json(), user=get_curr_user())

@app.route('/settings')
@login_required
@roles_required('admin')
def settings():
    return render_template('settings.html', container=get_mock_container(), data=parse_json(), user=get_curr_user())

@app.route('/getconfig')
@login_required
@roles_required('admin')
def get_config():
    tmstmp = time.strftime("%Y%m%d-%H%M%S")
    return send_file('config/test.txt',
                     mimetype='text/plain',
                     attachment_filename='minerctl_'+tmstmp+'.cfg',
                     as_attachment=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect('/')

@app.route('/user')
@login_required
@roles_required('admin')
def user_mgmt():
    return render_template('user.html', userbase=User.query.all(), user=get_curr_user())

# TODO remove this is just necessary for mocking content
def get_mock_container():
    container = {}

    for cont in range(16):
        container[cont] = []
        for miner in range(randint(20,120)):
            container[cont].append(miner + 1)

    return container
