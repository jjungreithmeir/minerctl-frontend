"""
This flask app acts as a frontend for flask-based JSON API which runs on a
microcontroller. The mc is connected to multiple mining rigs and is responsible
for controlling various variables regarding ventilation, resetting miners, etc.
"""
import os
import time
import json
from flask import Flask, render_template, send_file, request, \
    redirect, Response, url_for
from werkzeug.utils import secure_filename
from flask_security import Security, SQLAlchemyUserDatastore, \
    login_required, roles_required, url_for_security, \
    RegisterForm, current_user, utils
from wtforms import Form, BooleanField, StringField, PasswordField, \
    validators, SubmitField
from src.json_parser import parse_json, put_dict, resp_to_dict, put_str
from src.db_init import db, User, Role, Config, setup, add_or_update_user, \
    delete_user

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
APP.config['SECURITY_CONFIRMABLE'] = False

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
        'current_user': current_user,
        'is_admin': current_user.has_role('admin')
    }

# Views
@APP.route('/')
@login_required
def index():
    return render_template('index.html',
                           miners=parse_json(),
                           config=parse_json('/info'),
                           temp=parse_json('/temp'),
                           filter=parse_json('/filter'),
                           pid=parse_json('/pid'),
                           fans=parse_json('/fans'),
                           operation=parse_json('/mode'))

@APP.route('/settings', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def settings():
    """
    saved is of type str because there are three valid states
    '' ... show no toast
    'success' or 'failure' ... show appropriate message
    """
    saved = ''
    if request.method == 'POST':
        if request.form['action'] == 'save':
            error = put_dict(request.form)
            if error is None:
                saved='success'
            else:
                saved='failure'
        elif request.form['action'] == 'download':
            tmstmp = time.strftime("%Y%m%d-%H%M%S")
            data = request.form.copy()
            data.pop('action', None)
            return Response(
                json.dumps(data),
                mimetype='application/json',
                headers={
                'Content-Disposition':'attachment;filename=minerctl_'+tmstmp+'.cfg'}
            )
    return render_template('settings.html',
                           data=parse_json(),
                           config=parse_json('/info'),
                           saved=saved)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@APP.route('/upload', methods=['POST'])
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
            filename = 'current_conf.cfg'
            path = os.path.join(APP.config['UPLOAD_FOLDER'], filename)
            file.save(path)

            with open(path) as json_file:
                put_str(json_file)

            return redirect('/settings')
    return redirect('/')

class RegistrationForm(Form):
    email = StringField('username/email', [validators.DataRequired(),
                                           validators.Length(min=4, max=35)])
    password = PasswordField('password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('confirm password', [validators.DataRequired()])
    active = BooleanField('active', default=True)
    is_admin = BooleanField('is_admin', default=False)

@APP.route('/user', methods=['GET', 'POST'])
@roles_required('admin')
def user():
    form = RegistrationForm(request.form)
    if request.method == 'POST':
        data = resp_to_dict(request.form)

        if form.validate(): # equal to request.form['action'] == 'add':
            add_or_update_user(
                username=form.email.data,
                password=form.password.data,
                active=form.active.data,
                is_admin=form.is_admin.data)
        elif request.form.get('action') == 'delete':
            delete_user(data['username'])

    return render_template('user.html',
                           userbase=User.query.all(),
                           config=parse_json('/info'),
                           form=form)

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=80)
