import sys

import logging
import socket
import os
import hashlib

import yaml
from amon.utils.parsehost import parsehost

# dirname, dirname - climbs one dir higher
APPS_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(APPS_ROOT)


TESTING = True if 'test' in sys.argv else False
TRAVIS = True if os.getenv('TRAVIS') else False

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ACCOUNT_ID = 1

TIME_ZONE = 'UTC'

DATE_FORMAT = "d/m/Y"
DATETIME_FORMAT = "d/m/Y H:i"
DATE_FORMAT_ISO = "%d/%m/%Y"

SITE_ID = 1
USE_I18N = False
USE_L10N = False

APPEND_SLASH = True

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 86400


SECRET_KEY_UNIQUE = (socket.gethostname() + u'(71%ck467tyf=ty$c81r#96*!sy5bjg235^78y)&amp;u4vpy1$b$^').encode()
SECRET_KEY = hashlib.md5(SECRET_KEY_UNIQUE).hexdigest()


TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [
        APPS_ROOT + '/templates',
        APPS_ROOT + '/templates/notifications/_alerts/emails',
        APPS_ROOT + '/templates/notifications/_alerts/thirdparty',
    ],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.contrib.auth.context_processors.auth',
            'django.template.context_processors.debug',
            'django.template.context_processors.tz',
            'django.template.context_processors.request',
            "django.template.context_processors.static",
            'django.contrib.messages.context_processors.messages',
            'amon.apps.charts.context_processors.charts_global_variables',
        ],
        'builtins': [
            'amon.templatetags.url',
            'amon.templatetags.date',
            'amon.templatetags.setvar',
            'amon.templatetags.mongoid',
            'amon.templatetags.helpers',
            'amon.templatetags.math',
            'amon.templatetags.metrics',
            'amon.templatetags.baseurl',
            'amon.templatetags.formhelpers',
            'amon.templatetags.charts',
            'amon.templatetags.plugins'
        ],
    },
}]
MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'amon.apps.account.middleware.AccountMiddleware',
]


ROOT_URLCONF = 'amon.urls'


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'timezone_field',
    'kronos',

    'amon.templatetags',
    'amon.apps.dashboards',
    'amon.apps.servers',
    'amon.apps.alerts',
    'amon.apps.cloudservers',
    'amon.apps.notifications',
    'amon.apps.healthchecks',
    'amon.apps.charts',
    'amon.apps.users',
    'amon.apps.account',
)

REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    )
}

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_ARGS = [
    '--verbosity=3',
    '--with-yanc',
    '--with-timer',
    '--stop',
    '--exclude-dir=amon/apps/cloudservers',
    '--exclude-test=amon.apps.api.tests.cloudservers_test.TestCloudServersApi',
    '--with-coverage',
    '--cover-inclusive',
    '-x'
]


AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'amon.apps.account.backends.EmailAuthBackend',
]

AUTH_USER_MODEL = 'users.AmonUser'


API_RESULTS = {
    "ok": 200,
    "not-found": 404,
    "created": 201,
    "server-error": 500,
    "conflict": 409,
    "forbidden": 403,
    'unprocessable': 422
}


LOGIN_URL = '/account/login/'

SERVER_METRICS = {
    "": "",
    "1": "CPU",
    "2": "Memory",
    "3": "Loadavg",
    "5": "Disk"
}

PROCESS_METRICS = {"1": "CPU", "2": "Memory", "3": "Down"}
COMMON_METRICS = ["MB", "GB", "%"]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'


###########################
#
#     LOCAL SETTINGS
#
###########################
LOGFILE = '/var/log/amon/amonapp.log'
LOGFILE_REQUESTS = '/var/log/amon/amon_requests.log'

log_path = os.path.abspath(os.path.dirname(LOGFILE))
if not os.path.isdir(log_path):
    os.system('mkdir -p {}'.format(log_path))

log_request_path = os.path.abspath(os.path.dirname(LOGFILE_REQUESTS))
if not os.path.isdir(log_request_path):
    os.system('mkdir -p {}'.format(log_request_path))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/etc/opt/amon/amon.sqlite',
    }
}

config_path = "/etc/opt/amon/amon.yml"
config_file_path = os.path.abspath(os.path.dirname(config_path))
if not os.path.isdir(config_file_path):
    os.system('mkdir -p {}'.format(config_file_path))
if not os.path.isfile(os.path.abspath(config_path)):
    os.system('cp {}/amon.yml {}'.format(
        PROJECT_ROOT, os.path.abspath(config_path)
    ))

# Overwrite for the test suite
if TESTING:

    logging.disable(logging.CRITICAL)

    DATABASES = {
        'default': {
            'NAME': os.path.join(PROJECT_ROOT, 'amon_testing.sqlite'),
            'ENGINE': 'django.db.backends.sqlite3',
        },
    }

    config_path = os.path.join(PROJECT_ROOT, 'amon.yml')

    LOGFILE = os.path.join(PROJECT_ROOT, 'amoapp.log')
    LOGFILE_REQUESTS = os.path.join(PROJECT_ROOT, 'amoapp_requests.log')


try:
    with open(config_path, 'r') as f:
        config = yaml.load(f)
except yaml.YAMLError as exc:
    print(exc)
if config is None:
    config = {}  # Don't trigger exceptions if the config file is empty

MONGO_URL = config.get('mongo_uri', 'mongodb://localhost:27017')

HOST = config.get('host', '127.0.0.1')
STATIC_URL = config.get('static_url', None)


host_struct = parsehost(HOST)

ALLOWED_HOSTS = [
    host_struct.hostname,
    "127.0.0.1",
    "localhost",
    "*.localhost",
    "*.amon.cx"
]
HOST = host_struct.host
HOSTNAME = host_struct.hostname


if STATIC_URL is None:
    STATIC_URL = '{0}/static/'.format(HOST)

SSL = config.get('ssl', None)

#  Global retention period in days, overwrites settings set from the web interface
KEEP_DATA = config.get('keep_data', None)


# SMTP Settings - optionally store these in a config file
smtp = config.get('smtp', False)
EMAIL_USE_TLS = smtp.get('use_tls', False)
EMAIL_HOST = smtp.get('host', 'localhost')
EMAIL_PORT = smtp.get('port', 25)
EMAIL_HOST_USER = smtp.get('username', '')
EMAIL_HOST_PASSWORD = smtp.get('password', '')
DEFAULT_FROM_EMAIL = smtp.get('sent_from', EMAIL_HOST_USER)

if SSL or host_struct.scheme == 'https':
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

logging.getLogger("requests").setLevel(logging.WARNING)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        "simple": {
            "format": "%(levelname)s %(message)s"
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple"
        },
        'request_handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGFILE_REQUESTS,
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'simple',
        },
        'default': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGFILE,
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },

    },
    "loggers": {
        "": {
            "handlers": ["console", "default"],
            "level": "DEBUG",
        },
        'django': {
            'handlers': ['default', "console"],
            'level': 'ERROR',
            'propagate': False,
        },
        "django.request": {
            "handlers": ["request_handler"],
            'level': 'DEBUG',
            "propagate": True,
        },
    }
}




# Overwrite all settings with dev
try:
    from dev_settings import *
except:
    pass