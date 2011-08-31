import json

try:
	config_file = file('/etc/amon.conf').read()
	config = json.loads(config_file)
except:
	config = {}

#  Amon Defaults
BACKEND = config.get('backend', 'mongodb')

config_mongo = config.get('mongo', {})

MONGO = {
	'port': config_mongo.get('port', 27017),
	'host': config_mongo.get('host', 'localhost'),
	'user': config_mongo.get('user', ''),
	'password': config_mongo.get('password', ''),
	'database' : 'amon',
}

# 1 minute default
SYSTEM_CHECK_PERIOD = config.get('system_check_period', 60)

SYSTEM_CHECKS = config.get('system_checks', ['cpu', 'memory', 'disk', 'network', 'loadavg'])

PROCESS_CHECKS = config.get('process_checks', [])
