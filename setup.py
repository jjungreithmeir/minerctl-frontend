from setuptools import setup

setup(
    name='minerctl_frontend',
    version='1.0',
    py_modules=['controller'],
    install_requires=[
        'asn1crypto==0.24.0',
        'astroid==1.6.5',
        'Babel==2.6.0',
        'bcrypt==3.1.4',
        'blinker==1.4',
        'certifi==2018.4.16',
        'cffi==1.11.5',
        'chardet==3.0.4',
        'click==6.7',
        'cryptography==2.2.2',
        'Flask==1.0.2',
        'Flask-BabelEx==0.9.3',
        'Flask-JSGlue==0.3.1',
        'Flask-JWT-Extended==3.10.0',
        'Flask-Login==0.4.1',
        'Flask-Mail==0.9.1',
        'Flask-Principal==0.4.0',
        'Flask-Security==3.0.0',
        'Flask-Sijax==0.4.1',
        'Flask-SQLAlchemy==2.3.2',
        'Flask-WTF==0.14.2',
        'future==0.16.0',
        'idna==2.7',
        'isort==4.3.4',
        'itsdangerous==0.24',
        'Jinja2==2.10',
        'lazy-object-proxy==1.3.1',
        'MarkupSafe==1.0',
        'mccabe==0.6.1',
        'passlib==1.7.1',
        'pycparser==2.18',
        'PyJWT==1.6.4',
        'pylint==1.9.2',
        'pytz==2018.4',
        'requests==2.19.0',
        'Sijax==0.3.2',
        'six==1.11.0',
        'speaklater==1.3',
        'SQLAlchemy==1.2.8',
        'urllib3==1.23',
        'uWSGI==2.0.17.1',
        'Werkzeug==0.14.1',
        'wrapt==1.10.11',
        'WTForms==2.2.1'
    ],
    entry_points='''
        [console_scripts]
        frontend=wsgi:main
    ''',
)
