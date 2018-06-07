from flask import Flask, render_template, send_file, session, request, redirect
from werkzeug import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, roles_required, url_for_security, \
    RegisterForm, current_user, utils
from flask_admin import Admin
from flask_admin.contrib import sqla
from wtforms.fields import PasswordField
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
app.config['SECURITY_REGISTERABLE'] = True

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
    # __str__ is required by Flask-Admin, so we can have human-readable values for the Role when editing a User.
    # If we were using Python 2.7, this would be __unicode__ instead.
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

class Config(db.Model):
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    miner_number = db.Column(db.Integer())

# Add custom register form to app context as it is embedded into another page
@app.context_processor
def register_context():
    return {
        'url_for_security': url_for_security,
        'register_user_form': RegisterForm(),
    }

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Customized User model for SQL-Admin
class UserAdmin(sqla.ModelView):

    # Don't display the password on the list of Users
    column_exclude_list = ('password',)

    column_searchable_list = ['email']
    create_modal = True
    edit_modal = True

    # Don't include the standard password field when creating or editing a User (but see below)
    form_excluded_columns = ('password', 'last_login_at', 'last_login_ip', 'current_login_at', 'current_login_ip', 'login_count')

    # Automatically display human-readable names for the current and available Roles when creating or editing a User
    column_auto_select_related = True

    # Prevent administration of Users unless the currently logged-in user has the "admin" role
    def is_accessible(self):
        return current_user.has_role('admin')

    # On the form for creating or editing a User, don't display a field corresponding to the model's password field.
    # There are two reasons for this. First, we want to encrypt the password before storing in the database. Second,
    # we want to use a password field (with the input masked) rather than a regular text field.
    def scaffold_form(self):

        # Start with the standard form as provided by Flask-Admin. We've already told Flask-Admin to exclude the
        # password field from this form.
        form_class = super(UserAdmin, self).scaffold_form()

        # Add a password field, naming it "password2" and labeling it "New Password".
        form_class.password2 = PasswordField('New Password')
        return form_class

    # This callback executes when the user saves changes to a newly-created or edited User -- before the changes are
    # committed to the database.
    def on_model_change(self, form, model, is_created):

        # If the password field isn't blank...
        if len(model.password2):

            # ... then encrypt the new password prior to storing it in the database. If the password field is blank,
            # the existing password in the database will be retained.
            model.password = utils.encrypt_password(model.password2)


# Customized Role model for SQL-Admin
class RoleAdmin(sqla.ModelView):
    # Prevent administration of Roles unless the currently logged-in user has the "admin" role
    def is_accessible(self):
        return current_user.has_role('admin')

# Initialize Flask-Admin
admin = Admin(
    app,
    url='/mgmt'
)

# Add Flask-Admin views for Users and Roles
admin.add_view(UserAdmin(User, db.session))
admin.add_view(RoleAdmin(Role, db.session))

def get_curr_user():
    return User.query.filter_by(id=session["user_id"]).first().email

# Create a user to test withflask_security.utils
@app.before_first_request
def create_user():
    db.create_all()
    user_datastore.create_role(name='admin')
    if not user_datastore.get_user('user@email.com'):
        user_datastore.create_user(email='user@email.com', password=encrypt_password('password'), roles=['admin'])
    if not user_datastore.get_user('fake@email.com'):
        user_datastore.create_user(email='fake@email.com', password=encrypt_password('password1'))
    if not user_datastore.get_user('pseudo@email.com'):
        user_datastore.create_user(email='pseudo@email.com', password=encrypt_password('password2'))
    db.session.add(Config(miner_number=99))
    db.session.commit()

# Views
@app.route('/')
@login_required
def index():
    return render_template('index.html', container=get_mock_container(), data=parse_json(), user=get_curr_user(), config=Config.query.all())

@app.route('/settings')
@login_required
@roles_required('admin')
def settings():
    return render_template('settings.html', container=get_mock_container(), data=parse_json(), user=get_curr_user(), config=Config.query.all())

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

@app.route('/upload', methods=['POST'])
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

# @app.route('/user')
# @login_required
# @roles_required('admin')
# def user_mgmt():
#     return render_template('user.html', userbase=User.query.all(), user=get_curr_user())

# TODO remove this is just necessary for mocking content
def get_mock_container():
    container = {}

    for cont in range(16):
        container[cont] = []
        for miner in range(randint(20,120)):
            container[cont].append(miner + 1)

    return container
