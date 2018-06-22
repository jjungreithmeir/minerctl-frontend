from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin, SQLAlchemyUserDatastore
from flask_security.utils import encrypt_password
from src.config_reader import ConfigReader

DB = SQLAlchemy()

# Define models
ROLES_USERS = \
DB.Table('roles_users',
         DB.Column('user_id', DB.Integer(), DB.ForeignKey('user.id')),
         DB.Column('role_id', DB.Integer(), DB.ForeignKey('role.id')))

class Role(DB.Model, RoleMixin):
    id = DB.Column(DB.Integer(), primary_key=True)
    name = DB.Column(DB.String(80), unique=True)
    description = DB.Column(DB.String(255))

    def __str__(self):
        return self.name

    # __hash__ is required to avoid the exception
    # TypeError: unhashable type: 'Role' when saving a User
    def __hash__(self):
        return hash(self.name)

class User(DB.Model, UserMixin):
    id = DB.Column(DB.Integer, primary_key=True)
    email = DB.Column(DB.String(255), unique=True)
    password = DB.Column(DB.String(255))
    active = DB.Column(DB.Boolean())
    last_login_at = DB.Column(DB.DateTime())
    current_login_at = DB.Column(DB.DateTime())
    last_login_ip = DB.Column(DB.String(100))
    current_login_ip = DB.Column(DB.String(100))
    login_count = DB.Column(DB.Integer())
    roles = DB.relationship('Role', secondary=ROLES_USERS,
                            backref=DB.backref('users', lazy='dynamic'))
    def __str__(self):
        return self.email

def check_db_populated():
    try:
        return len(User.query.all())
    except:
        return False

def populate_db(user_datastore):
    DB.create_all()
    cfg_rdr = ConfigReader()

    user_datastore.create_role(
        name='admin',
        description='Admins are able to manage users and configure the \
        controller.')
    user_datastore.create_user(email=cfg_rdr.get_attr('username'),
                               password=
                               encrypt_password(cfg_rdr.get_attr('password')),
                               roles=['admin'])
    DB.session.commit()

def add_or_update_user(username, password, is_admin=False, active=True):
    user_datastore = SQLAlchemyUserDatastore(DB, User, Role)
    existing_user = user_datastore.find_user(email=username)
    if existing_user:
        user = User.query.filter_by(email=username).first()
        user.email = username
        user.password = encrypt_password(password)
        user.active = active
    else:
        user = user_datastore.create_user(
            email=username,
            password=encrypt_password(password),
            active=active)

    if is_admin:
        user_datastore.add_role_to_user(user, 'admin')
    DB.session.commit()

def delete_user(username):
    user_datastore = SQLAlchemyUserDatastore(DB, User, Role)
    user = user_datastore.find_user(email=username)
    user_datastore.delete_user(user)
    DB.session.commit()

def setup(user_datastore):
    if not check_db_populated():
        populate_db(user_datastore)
