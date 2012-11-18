import sys
try:
    import json
except ImportError:
    import simplejson as json

try:
    config_file = file('/etc/amon.conf').read()
    config = json.loads(config_file)
except Exception, e:
    print "There was an error in your configuration file (/etc/amon.conf)"
    raise e

#  Amon Defaults
BACKEND = config.get('backend', 'mongodb')

_backend = config.get('backend', {})
_mongo = _backend.get('mongo', {})
_web_app = config.get('web_app', {})

MONGO = {
    'port': _mongo.get('port', 27017),
    'host': _mongo.get('host', '127.0.0.1'),
    'user': _mongo.get('user', ''),
    'password': _mongo.get('password', ''),
    'database' : 'amon',
}

# 1 minute default
SYSTEM_CHECK_PERIOD = config.get('system_check_period', 60)

SYSTEM_CHECKS = ['cpu', 'memory', 'disk', 'network', 'loadavg']

if sys.platform == 'darwin':
    del SYSTEM_CHECKS[3] # Delete network check on macos

PROCESS_CHECKS = config.get('process_checks', [])


host = _web_app.get('host', 'http://127.0.0.1')

if not host.startswith('http'):
    host = "http://{0}".format(host)

WEB_APP = {
    'host': host,
    'port': _web_app.get('port', 2464)
}

ACL = config.get('acl', "False") # Expects string
key = config.get('secret_key', None)
PROXY = config.get('proxy', None) # Relative baseurl if true
ZEROMQ = config.get('zeromq', '127.0.0.1:5464') # TCP address for the ZeroMQ daemon

TIMEZONE = config.get('timezone','UTC')

if key != None and len(key) > 0:
    SECRET_KEY = key
else:
    SECRET_KEY = 'TGJKhSSeZaPZr24W6GlByAaLVe0VKvg8qs+8O7y=' #Don't break the dashboard

