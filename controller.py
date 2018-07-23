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
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import flask_sijax
from src.json_parser import JSONService
from src.db_init import DB, User, Role, setup, add_or_update_user, \
    delete_user
from src.config_reader import ConfigReader

APP = Flask(__name__)
JSONService = JSONService()

@APP.context_processor
def register_context():
    """
    Adds a couple of useful variables to the application context.

    :returns: current_user, url_for_security, register_user_form, is_admin
    """
    return {
        'url_for_security': url_for_security,
        'register_user_form': RegisterForm(),
        'current_user': current_user,
        'is_admin': current_user.has_role('admin')
    }

class SijaxHandler(object):
    """A container class for all Sijax handlers.
    Grouping all Sijax handler functions in a class
    (or a Python module) allows them all to be registered with
    a single line of code.
    """

    @staticmethod
    def get_config(obj_response):
        """
        Rewrites a couple of html elements. This is quite ugly as far as ajax
        updating goes but this is the only way which I've found.
        """
        cfg = JSONService.get('/cfg')
        for key, value in cfg['measurements'].items():
            obj_response.html('#card-measurement-' + key,
                              "<span id='card-measurement-'" + key + ">" +
                              str(value) + "</span>")
        obj_response.html('#card-pressure_diff',
                          "<span id='card-pressure_diff'>" +
                          str(cfg['pressure_diff']) + "</span>")
        obj_response.html('#card-rpm',
                          "<span id='card-rpm'>" +
                          str(cfg['rpm']) + "</span>")

        if cfg['pressure_diff'] >= cfg['threshold']:
            obj_response.html('#filter-sign',
                              "<i class='material-icons right blinking' \
                              title='CLEAN FILTER!'>warning</i>")
            obj_response.html('#filter-msg',
                              "<p class='font-bold'>FILTER REQUIRES CLEANING!\
                              </p>")
        else:
            obj_response.html('#filter-sign',
                              "<i class='material-icons right' \
                              title='filter does not need to be cleaned'>\
                              check</i>")
            obj_response.html('#filter-msg',"")

def _load_or_create_layout():
    """
    Checks whether a local layout.json file is present and then either parses
    or mocks the content of the json file.

    :returns: a nested list filled with the miner_ids
    """
    # first the layout.json has to be converted into an iterable dictionary
    layout = JSONService.read_json('config/layout.json')
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

    return local_config

@APP.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """
    Renders the index page for all logged in users.
    Some of the content of the index page is updated constantly through ajax
    requests which are handled by sijax.

    :returns: index view
    """
    if g.sijax.is_sijax_request:
        g.sijax.register_object(SijaxHandler)
        return g.sijax.process_request()

    miners = JSONService.get('/cfg')

    return render_template('index.html',
                           miners=JSONService.get('/cfg'),
                           local_config=_load_or_create_layout(),
                           config=JSONService.get('/info'),
                           temp=JSONService.get('/temp'),
                           filter=JSONService.get('/filter'),
                           pid=JSONService.get('/pid'),
                           fans=JSONService.get('/fans'),
                           operation=JSONService.get('/mode'))

@APP.route('/config', methods=['PUT'])
@roles_required('admin')
def config():
    """
    Writes the config to a local file.

    :returns: nothing, HTTP code 204
    """
    if request.method == 'PUT':
        JSONService.write_json(request.form)
    return '', 204

@APP.route('/commit', methods=['PUT'])
@roles_required('admin')
def commit():
    """
    PUTs the commit action to persist the microcontroller EEPROMs.

    :returns: nothing, HTTP code 204
    """
    if request.method == 'PUT':
        JSONService.put('/commit', data=request.form)
    return '', 204

@APP.route('/action', methods=['PATCH'])
def action():
    """
    PATCHes the action for the specific miner to the backend.

    :returns: nothing, HTTP code 204
    """
    if request.method == 'PATCH':
        JSONService.patch('/miner', request.args)

    return '', 204

@APP.route('/settings', methods=['GET', 'POST'])
@roles_required('admin')
def settings():
    """
    Provides and receives the settings. If the frontend requests it, the current
    configuration is streamed as a file response to the browser.

    :returns: settings view
    """
    if request.method == 'POST':
        if request.form['action'] == 'save':
            error = JSONService.patch('/cfg', data=request.form,
                                      exclude=['action', 'file'])
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
                           data=JSONService.get('/cfg'),
                           config=JSONService.get('/info'),
                           commit=JSONService.get('/commit'))

ALLOWED_EXTENSIONS = set(['cfg'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@APP.route('/upload', methods=['POST'])
@roles_required('admin')
def upload_file():
    """
    Saves file and sends the content to the backend to be parsed.

    :returns: redirects to the settings view
    """
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
                JSONService.patch_str('/cfg', json_file)

            return redirect('/settings')
    return redirect('/')

class RegistrationForm(Form):
    """
    WTForms class which is necessary for the registration functionality.
    """
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
    """
    Renders the user administration page which is responsible for viewing,
    deleting and adding new users.

    :returns: user view
    """
    form = RegistrationForm(request.form)
    if request.method == 'POST':
        data = JSONService.resp_to_dict(request.form)
        if form.validate() or form.is_update.data:
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
                           config=JSONService.get('/info'),
                           form=form)

@APP.errorhandler(500)
def page_not_found(_error):
    """
    Creating a specific HTML code 500 view as this may occur if the backend is
    unreachable which seems to be the most common error for a project like this.

    :returns: simple error page
    """
    return render_template('500.html'), 500

def _prepare_app():
    """
    Setup the initial APP values and initialize various flask plugins.

    :returns: flask app instance
    """
    # init JSGLUE. this is needed to query URLs in javascript
    _js_glue = JSGlue(APP)

    cfg_rdr = ConfigReader()

    APP.config['SECRET_KEY'] = cfg_rdr.get_attr('db_secret_key')
    APP.config['SQLALCHEMY_DATABASE_URI'] = cfg_rdr.get_attr('db_address')
    # needed because this functionality is already depricated
    APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # the salt is a workaround for a bug, as flask-security salts  passwords
    # automatically but somehow it requires and uses this config value which
    # breaks the login if the salt is individually unique (as a salt should be)
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

    APP.config['JWT_ALGORITHM'] = 'RS256'
    with open(cfg_rdr.get_attr('private_key_file_location'), 'rb') as file:
        APP.config['JWT_PRIVATE_KEY'] = file.read()
    JWT = JWTManager(APP)

    with APP.app_context():
        DB.init_app(APP)
        user_datastore = SQLAlchemyUserDatastore(DB, User, Role)
        _security = Security(APP, user_datastore)
        setup(user_datastore)
        rs256_token = create_access_token(str(current_user),
                                          expires_delta=False)

    APP.config['access_headers'] = {'Authorization': 'Bearer {}'
                                    .format(rs256_token)}
    JSONService.init(APP.config['access_headers'])

    return APP

def create_app():
    """
    Creates the app and starts it.
    """
    app = _prepare_app()
    app.run(host='0.0.0.0', port=80)

if __name__ == '__main__':
    create_app()
