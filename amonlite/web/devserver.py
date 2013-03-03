DEV_PATH = '/home/martin/amonlite'
import os
import sys
sys.path.insert(0, DEV_PATH)

from amonlite.web.server import application
import tornado.ioloop
import tornado.httpserver
from amonlite.core import settings
from tornado import autoreload

if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(int(settings.WEB_APP['port']))
    ioloop = tornado.ioloop.IOLoop().instance()
    autoreload.start(ioloop)
    ioloop.start()
