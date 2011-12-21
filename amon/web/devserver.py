import sys

if sys.platform == 'darwin':
	sys.path.insert(0, '/Users/User/amon')
else:
	sys.path.insert(0,'/home/martin/amon')


from amon.web.server import application
import tornado.ioloop
from amon.core import settings
from tornado import autoreload

if __name__ == "__main__":
	application.listen(int(settings.WEB_APP['port']), address='127.0.0.1')
	ioloop = tornado.ioloop.IOLoop().instance()
	autoreload.start(ioloop)
	ioloop.start()
