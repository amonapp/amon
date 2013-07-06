import sys
sys.path.insert(0,'/home/martin/amonone')

from amonone.web.server import application
import tornado.ioloop
from amonone.core import settings
from tornado import autoreload

if __name__ == "__main__":
    application.listen(int(settings.WEB_APP['port']))
    ioloop = tornado.ioloop.IOLoop().instance()
    autoreload.start(ioloop)
    ioloop.start()
