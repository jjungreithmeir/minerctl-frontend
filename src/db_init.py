from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin, SQLAlchemyUserDatastore, Security
from flask_security.utils import encrypt_password

db = SQLAlchemy()

# Define models
roles_users = db.Table('roles_users',
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
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    def __str__(self):
        return self.email

class Config(db.Model):
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    number_of_miners = db.Column(db.Integer())

def check_db_populated():
    try:
        return len(User.query.all())
    except:
        return False

# not needed anymore
def populate_db(user_datastore):
    db.create_all()

    with open('config/initial.config') as file:
        content = file.read().splitlines()

    cfg_username = content[4].split('=')[1]
    cfg_password = content[5].split('=')[1]
    cfg_miner_number = content[6].split('=')[1]

    user_datastore.create_role(name='admin', description='Admins are able to manage users and configure the controller.')
    user_datastore.create_user(email=cfg_username, password=encrypt_password(cfg_password), roles=['admin'])
    db.session.add(Config(number_of_miners=cfg_miner_number))
    db.session.commit()

def update_config(dictionary):
    db.session.query(Config).filter_by(id=1).update(dictionary)
    db.session.commit()

def setup(db, user_datastore):

    if not check_db_populated():
        populate_db(user_datastore)
