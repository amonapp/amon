#  Amon Defaults
BACKEND = 'mongodb'

MONGO = {
	'port': 27017,
	'host': 'localhost',
	'user': '',
	'password': '',
	'database' : 'amon',
}

# 1 minute default
SYSTEM_CHECK_PERIOD = 60

SYSTEM_CHECKS = ('cpu', 'memory', 'disk', 'network', 'loadavg')

PROCESS_CHECKS = ('mongo', )
