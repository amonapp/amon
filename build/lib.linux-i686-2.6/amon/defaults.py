#  Amon Defaults
BACKEND = 'mongodb'

MONGO = {
	'port': 27017,
	'host': 'localhost',
	'user': '',
	'password': '',
	'database' : 'amon',
	'valid_system_collections': ('cpu', 'memory', 'disk', 'network', 'loadavg')
}

# 1 minute default
SYSTEM_CHECK_PERIOD = 60


ACTIVE_CHECKS = ('cpu', 'memory', 'disk', 'network', 'loadavg')
