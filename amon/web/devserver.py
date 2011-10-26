from server import application
import tornado.ioloop
from amon.core import settings

if __name__ == "__main__":
	application.listen(int(settings.WEB_APP['port']))
	tornado.ioloop.IOLoop.instance().start()
