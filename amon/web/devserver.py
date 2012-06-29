DEV_PATH = '/home/martin/amon'
import os
import sys
sys.path.insert(0, DEV_PATH)

from amon.web.server import application
import tornado.ioloop
import tornado.httpserver
from amon.core import settings
from tornado import autoreload

#ssl_options={ 
    #"certfile": os.path.join(DEV_PATH, "amon.crt"), 
    #"keyfile": os.path.join(DEV_PATH, "amon.key"), 
#}

if __name__ == "__main__":
    #http_server = tornado.httpserver.HTTPServer(application, ssl_options=ssl_options)
    #http_server.listen(int(settings.WEB_APP['port']))
    application.listen(int(settings.WEB_APP['port']))
    ioloop = tornado.ioloop.IOLoop().instance()
    autoreload.start(ioloop)
    ioloop.start()
