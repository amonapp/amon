import sys
import os

amon_dir = os.sep.join(os.path.abspath( __file__ ).split(os.sep)[:-3])
sys.path.insert(0, amon_dir)

from amon.web.server import application
import tornado.ioloop
from amon.core import settings
from tornado import autoreload

if __name__ == "__main__":
	application.listen(int(settings.WEB_APP['port']))
	ioloop = tornado.ioloop.IOLoop().instance()
	autoreload.start(ioloop)
	ioloop.start()
