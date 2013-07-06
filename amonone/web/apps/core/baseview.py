import os
import tornado.web
from datetime import datetime
from amonone.core import settings
from amonone.web.apps.core.models import server_model
from amonone.web.libs.session import MongoDBSession
from amonone.web.template import render as jinja_render
from amonone.web.apps.auth.acl import (
		check_permissions, 
		all_servers_for_user,
		)

class BaseView(tornado.web.RequestHandler):

	def initialize(self):
		self.session = self._create_session()
		self.now = datetime.utcnow()
		self.acl = settings.ACL		


		try:
			current_page = self.current_page
		except:
			current_page = ''

		# Template variables. Passing that dictionary to Jinja
		self.template_vars = {
				"user": self.current_user,
				"url": self.request.uri,
				"current_page": current_page,
				"xsrf": self.xsrf_form_html(),
				}

		super(BaseView, self).initialize()

	# Overwrite the xsrf check for the test suite
	def check_xsrf_cookie(self):
		try:
			test = os.environ['AMON_TEST_ENV']
		except:
			super(BaseView, self).check_xsrf_cookie()

	def get_current_user(self):

		try: 
			if os.environ['AMON_TEST_ENV'] == 'True':
				return {"username": "testuser", "type": "admin"}
		except:
			pass

		# Check is the page is in the list with pages that a read-only by default
		current_page = self.request.uri.split('?')
		try:
			url = current_page[0]
		except:
			url = self.request.uri

		id = False
		list = ['/', '/system', '/processes']
		if url in list:
			try:
				url_params =  self.request.uri.split('=')
				id = url_params[-1]
				id = False if id in list else id # If there are no paramaters in the url, the page id is False
			except:
				id = False
	
		try:
			user = self.session['user']
		except KeyError:
			return None

		permissions = check_permissions(id, url, user)

		if permissions is True:
			return user

		return None
	  
	def write_error(self, status_code, **kwargs):
		error_trace = None

		if "exc_info" in kwargs:
			import traceback

		error_trace= ""
		for line in traceback.format_exception(*kwargs["exc_info"]):
			error_trace += line 

		self.render("error.html", 
				status_code=status_code,
				error_trace=error_trace,
				unread_values=None)

	def finish(self, chunk = None):
		if self.session is not None and self.session._delete_cookie:
			self.clear_cookie('amonplus_session_id')
		elif self.session is not None:
			self.session.refresh() # advance expiry time and save session
			self.set_secure_cookie('amonplus_session_id', self.session.session_id, expires_days=None, expires=self.session.expires)

		super(BaseView, self).finish(chunk = chunk)


	def _create_session(self):
		session_id = self.get_secure_cookie('amonplus_session_id')

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


	def get_session_key_and_delete(self, key):
		
		value = self.get_session_key(key)
		self.delete_session_key(key)

		return value

	def get_session_key(self, key):
		try:
			return self.session[key]
		except:
			return None

	def delete_session_key(self, key):
		try:
			del self.session[key]
		except:
			pass


	def paginate(self, data, page=None):
		page_size = 100
		
		page = 1 if page == None else int(page)
		page = 1 if page == 0 else page
		
		rows = len(data)
		total_pages = rows/page_size
		total_pages = 1 if total_pages == 0 else total_pages
		
		page = total_pages if page > total_pages else page

		from_ = page_size * (page - 1)
		to = from_+page_size

		result = data[from_:to]
		
		pagination = {
				"pages": total_pages, 
				"current_page": page,
				"result": result 
		}
		
		return pagination


	def render(self, template, *args, **kwargs):
		kwargs['app'] = self.template_vars
		rendered_template = jinja_render(template, *args, **kwargs)

		self.write(rendered_template)

