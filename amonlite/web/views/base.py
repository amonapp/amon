import tornado.web
from datetime import datetime
from os import getenv
from amon.core import settings
from amon.web.models import unread_model
from amon.web.libs.session import MongoDBSession
from amon.web.template import render as jinja_render
from amon import __version__

class BaseView(tornado.web.RequestHandler):

    def initialize(self):
        self.session = self._create_session()
        self.now = datetime.utcnow()
        self.acl = settings.ACL

        # Unread logs and exceptions -> in the sidebar
        unread_values = unread_model.get_unread_values()        
        
        # Template variables. Passing that dictionary to Jinja
        self.template_vars = {
            "user": self.current_user,
            "unread_values": unread_values,
            "url": self.request.uri,
            "version": __version__
        }

        super(BaseView, self).initialize()

    def get_current_user(self):
        # For the testing suite
        if getenv('AMON_ENV_HTTP_TEST', None) == 'test':
            return 1

        if self.acl == 'True':
            try:
                return self.session['user']
            except KeyError:
                return None
        else:
            # Delete the cookie with user data, so the next time acl is set to true it will 
            # redirect to the login page
            try:
                del self.session['user']
            except:
                pass

            # Check is the page is in the list with pages that a read-only by default
            current_page = self.request.uri.split('?')
            try:
                url = current_page[0]
            except:
                url = self.request.uri

            list = ['/', '/exceptions', '/logs', '/system', '/processes']
            if url in list:
                return 1
            else:
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
            self.clear_cookie('amon_session_id')
        elif self.session is not None:
            self.session.refresh() # advance expiry time and save session
            self.set_secure_cookie('amon_session_id', self.session.session_id, expires_days=None,
                                       expires=self.session.expires,)
            
        super(BaseView, self).finish(chunk = chunk)


    def _create_session(self):
        session_id = self.get_secure_cookie('amon_session_id')

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

    
    def render(self, template, *args, **kwargs):
        kwargs['app'] = self.template_vars
        rendered_template = jinja_render(template, *args, **kwargs)

        self.write(rendered_template)

