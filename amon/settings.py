import sys

import logging
import socket
import os
import hashlib

import yaml
from amon.utils.parsehost import parsehost

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))  # dirname, dirname - climbs one dir higher

TESTING = True if 'test' in sys.argv else False
TRAVIS = True if os.getenv('TRAVIS') else False

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ACCOUNT_ID = 1

TIME_ZONE = None

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
        PROJECT_ROOT + '/templates',
        PROJECT_ROOT + '/templates/notifications/_alerts/emails',
        PROJECT_ROOT + '/templates/notifications/_alerts/thirdparty',
    ],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.contrib.auth.context_processors.auth',
            'django.core.context_processors.debug',
            'django.core.context_processors.tz',
            'django.contrib.messages.context_processors.messages',
            'django.core.context_processors.request',
            "django.core.context_processors.static",
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


LOGIN_URL = '/account/login'
LOGFILE = '/var/log/amon/amonapp.log'
LOGFILE_REQUESTS = '/var/log/amon/amon_requests.log'


logging.getLogger("requests").setLevel(logging.WARNING)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
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


SERVER_METRICS = {
    "": "",
    "1": "CPU",
    "2": "Memory",
    "3": "Loadavg",
    "5": "Disk"
}

PROCESS_METRICS = {"1": "CPU", "2": "Memory", "3": "Down"}
COMMON_METRICS = ["MB", "GB", "%"]

EMAIL_BACKEND = 'amon.apps.notifications.mail.backends.AmonEmailBackend'

###########################
#
#     LOCAL SETTINGS
#
###########################
default_config_path = "/etc/opt/amon/amon.yml"
try:
    with open(default_config_path, 'r') as f:
        config = yaml.load(f)
except yaml.YAMLError as exc:
    print(exc)
if config is None:
    config = {}  # Don't trigger exceptions if the config file is empty

MONGO_URL = config.get('mongo_uri', 'mongodb://localhost:27017')

HOST = config.get('host', '127.0.0.1')
STATIC_URL = config.get('static_url', None)

host_struct = parsehost(HOST)

ALLOWED_HOSTS = [host_struct.hostname]
HOST = host_struct.host
HOSTNAME = host_struct.hostname


if STATIC_URL is None:
    STATIC_URL = '{0}/static/'.format(HOST)


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/etc/opt/amon/amon.sqlite',
    }
}

if TESTING:

    logging.disable(logging.CRITICAL)

    DATABASES = {
        'default': {
            'NAME': os.path.join(PROJECT_ROOT, 'amon_testing.sqlite'),
            'ENGINE': 'django.db.backends.sqlite3',
        },
    }

SSL = config.get('ssl', None)

#  Global retention period in days, overwrites settings set from the web interface
KEEP_DATA = config.get('keep_data', None)


# SMTP Settings - optionally store these in a config file
SMTP = config.get('smtp', False)

if SSL or host_struct.scheme == 'https':
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


# Overwrite all settings with dev
try:
    from dev_settings import *
except:
    pass
