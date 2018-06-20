# TODO refactor this hot spaghetti code mess
from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin, SQLAlchemyUserDatastore, Security
from flask_security.utils import encrypt_password
from src.config_reader import ConfigReader

db = SQLAlchemy()

# Define models
ROLES_USERS = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name

    # __hash__ is required to avoid the exception TypeError: unhashable type: 'Role' when saving a User
    def __hash__(self):
        return hash(self.name)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(100))
    current_login_ip = db.Column(db.String(100))
    login_count = db.Column(db.Integer())
    roles = db.relationship('Role', secondary=ROLES_USERS,
                            backref=db.backref('users', lazy='dynamic'))
    def __str__(self):
        return self.email

def check_db_populated():
    try:
        return len(User.query.all())
    except:
        return False

# not needed anymore
def populate_db(user_datastore):
    db.create_all()

    cfg_rdr = ConfigReader()

    user_datastore.create_role(
        name='admin',
        description='Admins are able to manage users and configure the \
        controller.')
    user_datastore.create_user(email=cfg_rdr.get_attr('username'),
                               password=
                               encrypt_password(cfg_rdr.get_attr('password')),
                               roles=['admin'])
    db.session.commit()

def add_or_update_user(username, password, is_admin=False, active=True):
    USER_DATASTORE = SQLAlchemyUserDatastore(db, User, Role)
    existing_user = USER_DATASTORE.find_user(email=username)
    if existing_user:
        user = User.query.filter_by(email=username).first()
        user.email=username
        user.password=encrypt_password(password)
        user.active=active
    else:
        user = USER_DATASTORE.create_user(
            email=username,
            password=encrypt_password(password),
            active=active)

    if is_admin:
        USER_DATASTORE.add_role_to_user(user, 'admin')
    db.session.commit()

def delete_user(username):
    USER_DATASTORE = SQLAlchemyUserDatastore(db, User, Role)
    user = USER_DATASTORE.find_user(email=username)
    USER_DATASTORE.delete_user(user)
    db.session.commit()

def setup(db, user_datastore):

    if not check_db_populated():
        populate_db(user_datastore)
