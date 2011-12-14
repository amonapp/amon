import tornado.web
from amon.web.template import render
from datetime import datetime
from amon.web.models import common_model
from amon.web.libs.session import MongoDBSession
from amon.core import settings

class BaseView(tornado.web.RequestHandler):

	def initialize(self):
		self.session = self._create_session()
		self.now = datetime.now()

		self.unread_values = common_model.get_unread_values()		
		super(BaseView, self).initialize()

	def get_current_user(self):
		acl = settings.ACL
		if acl == 'True':
			try:
				self.session['user']
				return 1
			except KeyError:
				return None
		else:
			return 1

	def write_error(self, status_code, **kwargs):
		error_trace = None

		if "exc_info" in kwargs:
			import traceback
		
		error_trace= ""
		for line in traceback.format_exception(*kwargs["exc_info"]):
			error_trace += line 

		_template = render(template="error.html", 
				status_code=status_code,
				error_trace=error_trace,
				unread_values=None)

		self.write(_template)

	def finish(self, chunk = None):
		
		if self.session is not None and self.session._delete_cookie:
			self.clear_cookie('session_id')
		elif self.session is not None:
			self.session.refresh() # advance expiry time and save session
			self.set_secure_cookie('session_id', self.session.session_id, expires_days=None,
                                       expires=self.session.expires,)
			
		super(BaseView, self).finish(chunk = chunk)


	def _create_session(self):
		session_id = self.get_secure_cookie('session_id')

		kw = {'security_model': [],
				'duration': self.settings['session']['duration'],
				'ip_address': self.request.remote_ip,
				'user_agent': self.request.headers.get('User-Agent'),
				'regeneration_interval': self.settings['session']['regeneration_interval']
				}
		
		new_session = None
		old_session = None

		old_session = MongoDBSession.load(session_id)

		if old_session is None or old_session._is_expired(): # create new session
			new_session = MongoDBSession(**kw)

		if old_session is not None:
			if old_session._should_regenerate():
				old_session.refresh(new_session_id=True)
			return old_session

		return new_session	

	# Deletes a key from a dictionary
	def delete_key(self, dict_key):
		try: 
			del dict_key
		except KeyError:
			pass

		return False

	#def save_session(self):
		#if self.session is not None and self.session._delete_cookie:
			#self.clear_cookie('session_id')
		#elif self.session is not None:
			#self.session.refresh() # advance expiry time and save session
			#self.set_secure_cookie('session_id', self.session.session_id, expires=self.session.expires)


