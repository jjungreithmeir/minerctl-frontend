from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required
import os
from src.json_parser import parse_json
# TODO Remove random
from random import randint

# Create app
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'n0b0dy-c0u1d-guess-th15'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
# TODO the salt is a workaround for a bug, as flask-security salts the passwords automatically
# but somehow it doesn't notice it.
app.config['SECURITY_PASSWORD_SALT'] = os.urandom(1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Create a user to test with
@app.before_first_request
def create_user():
    db.create_all()
    user_datastore.create_user(email='user@email.com', password='password')
    db.session.commit()

# Views
@app.route('/')
@login_required
def index():
    return render_template('index.html', container=get_mock_container(), data=parse_json())

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html', container=get_mock_container(), data=parse_json())

# TODO remove this is just necessary for mocking content
def get_mock_container():
    container = {}

    for cont in range(16):
        container[cont] = []
        for miner in range(randint(20,120)):
            container[cont].append(miner + 1)

    return container
