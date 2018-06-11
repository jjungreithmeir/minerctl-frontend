"""
This flask app acts as a frontend for flask-based JSON API which runs on a
microcontroller. The mc is connected to multiple mining rigs and is responsible
for controlling various variables regarding ventilation, resetting miners, etc.
"""
import os
import time
from flask import Flask, render_template, send_file, request, \
    redirect, flash
from werkzeug.utils import secure_filename
from flask_security import Security, SQLAlchemyUserDatastore, \
    login_required, roles_required, url_for_security, \
    RegisterForm, current_user, utils
from flask_admin import Admin
from flask_admin.contrib import sqla
from wtforms.fields import PasswordField
from src.json_parser import parse_json
from src.db_init import db, User, Role, Config, setup

# Create APP
APP = Flask(__name__)

APP.config['SECRET_KEY'] = 'n0b0dy-c0u1d-gue55-th15'
APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///config/database.sqlite3'
# needed because this functionality is already depricated
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# the salt is a workaround for a bug, as flask-security salts  passwords
# automatically but somehow it requires and uses this config value which breaks
# the login if the salt is individually unique (as a salt should be)
APP.config['SECURITY_PASSWORD_SALT'] = 'fake_salt'
APP.config['SECURITY_TRACKABLE'] = True
APP.config['SECURITY_REGISTERABLE'] = True

APP.config['UPLOAD_FOLDER'] = 'config'
# max upload size is 50 KB
APP.config['MAX_CONTENT_LENGTH'] = 50 * 1024
ALLOWED_EXTENSIONS = set(['cfg'])

with APP.app_context():
    db.init_app(APP)
    USER_DATASTORE = SQLAlchemyUserDatastore(db, User, Role)
    SECURITY = Security(APP, USER_DATASTORE)
    setup(db, USER_DATASTORE)

@APP.context_processor
def register_context():
    return {
        'url_for_security': url_for_security,
        'register_user_form': RegisterForm(),
        'current_user': current_user
    }

class UserAdmin(sqla.ModelView):
    """
    Customized User model for SQL-Admin
    """

    # Don't display the password on the list of Users
    column_exclude_list = ('password',)
    column_searchable_list = ['email']

    create_modal = True
    edit_modal = True
    form_excluded_columns = ('password', 'last_login_at', 'last_login_ip',
                             'current_login_at', 'current_login_ip',
                             'login_count')

    column_auto_select_related = True

    def is_accessible(self):
        return current_user.has_role('admin')

    def scaffold_form(self):
        form_class = super(UserAdmin, self).scaffold_form()
        form_class.password2 = PasswordField('New Password')
        return form_class

    def on_model_change(self, form, model, is_created):

        # If the password field isn't blank...
        if model.password2:
            # the existing password in the database will be retained.
            model.password = utils.encrypt_password(model.password2)

# Initialize Flask-Admin
ADMIN = Admin(
    APP,
    url='/mgmt'
)

# Add Flask-Admin views for Users and Roles
ADMIN.add_view(UserAdmin(User, db.session))

# Views
@APP.route('/')
@login_required
def index():
    return render_template('index.html', data=parse_json(), config=Config.query.all())

@APP.route('/settings')
@login_required
@roles_required('admin')
def settings():
    return render_template('settings.html', data=parse_json(), config=Config.query.all())

@APP.route('/getconfig')
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

@APP.route('/upload', methods=['POST'])
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
            file.save(os.path.join(APP.config['UPLOAD_FOLDER'], filename))
            return redirect('/settings')
    return redirect('/')

@APP.route('/user')
@login_required
@roles_required('admin')
def user():
    return render_template('user.html', userbase=User.query.all())
