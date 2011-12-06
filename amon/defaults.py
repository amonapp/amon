try:
    import json
except ImportError:
    import simplejson as json

try:
	config_file = file('/etc/amon.conf').read()
	config = json.loads(config_file)
except:
	config = {}

#  Amon Defaults
BACKEND = config.get('backend', 'mongodb')

_backend = config.get('backend', {})
_mongo = _backend.get('mongo', {})
_web_app = config.get('web_app', {})

MONGO = {
	'port': _mongo.get('port', 27017),
	'host': _mongo.get('host', 'localhost'),
	'user': _mongo.get('user', ''),
	'password': _mongo.get('password', ''),
	'database' : 'amon',
}

# 1 minute default
SYSTEM_CHECK_PERIOD = config.get('system_check_period', 60)

SYSTEM_CHECKS = config.get('system_checks', ['cpu', 'memory', 'disk', 'network', 'loadavg'])

PROCESS_CHECKS = config.get('process_checks', [])

WEB_APP = {
	'host': _web_app.get('host', 'http://127.0.0.1'),
	'port': _web_app.get('port', 2464)
}

ACL = config.get('acl', False)
SECRET = config.get('secret', False)
