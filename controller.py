"""
This flask app acts as a frontend for flask-based JSON API which runs on a
microcontroller. The mc is connected to multiple mining rigs and is responsible
for controlling various variables regarding ventilation, resetting miners, etc.
"""
import os
import time
import json
from flask import Flask, render_template, request, \
    redirect, Response, url_for, flash, g
from flask_security import Security, SQLAlchemyUserDatastore, \
    login_required, roles_required, url_for_security, \
    RegisterForm, current_user
from wtforms import Form, BooleanField, StringField, PasswordField, \
    validators, HiddenField
from flask_jsglue import JSGlue
import flask_sijax
from src.json_parser import get, resp_to_dict, patch_str, \
    patch, write_json, read_json
from src.db_init import db, User, Role, setup, add_or_update_user, \
    delete_user
from src.config_reader import ConfigReader

APP = Flask(__name__)

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
    # first the layout.json has to be converted into an iterable dictionary
    layout = read_json()
    local_config = {'max_number_of_racks': 12}
    if layout is None:
        local_config['number_of_racks'] = 12
        racks = []
        counter = 0
        for rack in range(12):
            rack = []
            for _ in range(10):
                rack.append(counter)
                counter += 1
            racks.append(rack)
        local_config['racks'] = racks
    else:
        local_config['number_of_racks'] = int(layout.pop('number_of_racks'))
        racks = []
        for rack, string in layout.items():
            temp = string.replace('rack=', '')
            ids = temp.split('&')
            # casting all strs to ints
            ids = list(map(int, ids))
            racks.append(ids)
        local_config['racks'] = racks

    return render_template('index.html',
                           miners=get(),
                           local_config=local_config,
                           config=get('/info'),
                           temp=get('/temp'),
                           filter=get('/filter'),
                           pid=get('/pid'),
                           fans=get('/fans'),
                           operation=get('/mode'))

@APP.route('/config', methods=['PUT'])
@roles_required('admin')
def config():
    if request.method == 'PUT':
        write_json(request.form)
    return '', 204

@APP.route('/action', methods=['PATCH'])
def action():
    if request.method == 'PATCH':
        patch(request.args)

    return '', 204

@APP.route('/settings', methods=['GET', 'POST'])
@roles_required('admin')
def settings():
    if request.method == 'POST':
        if request.form['action'] == 'save':
            error = patch(data=request.form, exclude=['action', 'file'],
                          resource='/cfg')
            if error is None:
                flash('success')
            else:
                flash('failure')
        elif request.form['action'] == 'download':
            tmstmp = time.strftime("%Y%m%d-%H%M%S")
            data = request.form.copy()
            data.pop('action', None)
            return Response(
                json.dumps(data),
                mimetype='application/json',
                headers={
                    'Content-Disposition':'attachment;filename=minerctl_' +
                                          tmstmp + '.cfg'}
            )
        # POST/Redirect/GET
        return redirect(url_for('settings'))
    return render_template('settings.html',
                           data=get(),
                           config=get('/info'))

ALLOWED_EXTENSIONS = set(['cfg'])
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
                patch_str(json_file)

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
    is_update = HiddenField("is_update")

@APP.route('/user', methods=['GET', 'POST'])
@roles_required('admin')
def user():
    form = RegistrationForm(request.form)
    if request.method == 'POST':
        data = resp_to_dict(request.form)
        if form.validate() or form.is_update.data: # equal to request.form['action'] == 'add':
            add_or_update_user(
                username=form.email.data,
                password=form.password.data,
                active=form.active.data,
                is_admin=form.is_admin.data)
        elif request.form.get('action') == 'delete':
            delete_user(data['username'])
        # POST/Redirect/GET
        return redirect(url_for('user'))

    return render_template('user.html',
                           userbase=User.query.all(),
                           config=get('/info'),
                           form=form)

@APP.errorhandler(500)
def page_not_found(error):
    # note that we set the 404 status explicitly
    return render_template('500.html'), 500

def prepare_app():
    # init JSGLUE. this is needed to query URLs in javascript
    js_glue = JSGlue(APP)

    cfg_rdr = ConfigReader()

    APP.config['SECRET_KEY'] = cfg_rdr.get_attr('db_secret_key')
    APP.config['SQLALCHEMY_DATABASE_URI'] = cfg_rdr.get_attr('db_address')
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

    path = os.path.join('.', os.path.dirname(__file__), 'static/js/sijax/')

    APP.config['SIJAX_STATIC_PATH'] = path
    APP.config['SIJAX_JSON_URI'] = '/static/js/sijax/json2.js'
    flask_sijax.Sijax(APP)

    with APP.app_context():
        db.init_app(APP)
        user_datastore = SQLAlchemyUserDatastore(db, User, Role)
        security = Security(APP, user_datastore)
        setup(db, user_datastore)

    return APP

def create_app():
    app = prepare_app()
    app.run(host='0.0.0.0', port=80)

if __name__ == '__main__':
    create_app()
