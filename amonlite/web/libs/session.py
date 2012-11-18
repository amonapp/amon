# -*- coding: utf-8 -*-

"""
Sessions module for the Tornado framework.
Milan Cermak <milan.cermak@gmail.com> 

USAGE:
======

Every session object can be handled as a dictionary:
    self.session[key] = value
    var = self.session[key]

The session data is saved automatically for you when the request
handler finishes. 

Two utility functions, invalidate() and refresh() are available to
every session object. Read their documentation to learn more.

The application provider is responsible for removing stale, expired
sessions from the storage. However, he can use the delete_expired()
function provided with every storage class except Memcached, which
knows when a session expired and removes it automatically.


SETTINGS:
=========

The session module introduces new settings available to the
application:

session_age: how long should the session be valid (applies also to cookies);
             the value can be anything an integer, long, string or datetime.timedelta;
             integer, long and string are meant to represent seconds,
             default is 900 seconds (15 mins);
             check out _expires_at for additional info

session_regeneration_interval: period in seconds, after which the session_id should be
                               regenerated; when the session creation time + period
                               exceed current time, a new session is stored
                               server-side (the sesion data remains unchanged) and
                               the client cookie is refreshed; the old session
                               is no longer valid
                               session regeneration is used to strenghten security
                               and prevent session hijacking; default interval
                               is 4 minutes
                               the setting accepts integer, string or timedelta values,
                               read _next_regeneration_at() documentation for more info

session_cookie_name: the name of the cookie, which stores the session_id;
                     default is 'session_id'

session_cookie_path: path attribute for the session cookie;
                     default is '/'

session_cookie_domain: domain attribute for the session cookie;
                       default is None

"""
import base64
import collections
import datetime
import os
import cPickle as pickle
import time
from amon.backends.mongodb import MongoBackend

class BaseSession(collections.MutableMapping):
    """The base class for the session object. Work with the session object
    is really simple, just treat is as any other dictionary:

    class Handler(tornado.web.RequestHandler):
        def get(self):
            var = self.session['key']
            self.session['another_key'] = 'value'

    Session is automatically saved on handler finish. Session expiration
    is updated with every request. If configured, session ID is
    regenerated periodically.

    The session_id attribute stores a unique, random, 64 characters long
    string serving as an indentifier.

    To create a new storage system for the sessions, subclass BaseSession
    and define save(), load() and delete(). For inspiration, check out any
    of the already available classes and documentation to aformentioned functions."""
    def __init__(self, session_id=None, data=None, security_model=[], expires=None,
                 duration=None, ip_address=None, user_agent=None,
                 regeneration_interval=None, next_regeneration=None, **kwargs):
        # if session_id is True, we're loading a previously initialized session
        if session_id:
            self.session_id = session_id
            self.data = data
            self.duration = duration
            self.expires = expires
            self.dirty = False
        else:
            self.session_id = self._generate_session_id()
            self.data = {}
            self.duration = duration
            self.expires = self._expires_at()
            self.dirty = True

        self.ip_address = ip_address
        self.user_agent = user_agent
        self.security_model = security_model
        self.regeneration_interval = regeneration_interval
        self.next_regeneration = next_regeneration or self._next_regeneration_at()
        self._delete_cookie = False

    def __repr__(self):
        return '<session id: %s data: %s>' % (self.session_id, self.data)

    def __str__(self):
        return self.session_id

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
        self.dirty = True

    def __delitem__(self, key):
        del self.data[key]
        self.dirty = True

    def keys(self):
        return self.data.keys()

    def __iter__(self):
        return self.data.__iter__()

    def __len__(self):
        return len(self.data.keys())

    def _generate_session_id(cls):
        return os.urandom(16).encode('hex') 

    def _is_expired(self):
        """Check if the session has expired."""
        if self.expires is None: # never expire
            return False 
        return datetime.datetime.utcnow() > self.expires

    def _expires_at(self):
        """Find out the expiration time. Returns datetime.datetime."""
        v = self.duration
        if v is None: # never expire
            return None
        elif isinstance(v, datetime.timedelta):
            pass
        elif isinstance(v, (int, long)):
            self.duration =  datetime.timedelta(seconds=v)
        elif isinstance(v, basestring):
            self.duration = datetime.timedelta(seconds=int(v))
        else:
            self.duration = datetime.timedelta(seconds=900) # 15 mins

        return datetime.datetime.utcnow() + self.duration

    def _serialize_expires(self):
        """ Determines what value of expires is stored to DB during save()."""
        if self.expires is None:
            return None
        else:
            return int(time.mktime(self.expires.timetuple()))

    def _should_regenerate(self):
        """Determine if the session_id should be regenerated."""
        if self.regeneration_interval is None: # never regenerate
            return False
        return datetime.datetime.utcnow() > self.next_regeneration

    def _next_regeneration_at(self):
        """Return a datetime object when the next session id regeneration
        should occur."""
        # convert whatever value to an timedelta (period in seconds)
        # store it in self.regeneration_interval to prevent
        # converting in later calls and return the datetime
        # of next planned regeneration
        v = self.regeneration_interval
        if v is None: # never regenerate
            return None
        elif isinstance(v, datetime.timedelta):
            pass
        elif isinstance(v, (int, long)):
            self.regeneration_interval = datetime.timedelta(seconds=v)
        elif isinstance(v, basestring):
            self.regeneration_interval = datetime.timedelta(seconds=int(v))
        else:
            self.regeneration_interval = datetime.timedelta(seconds=240) # 4 mins

        return datetime.datetime.utcnow() + self.regeneration_interval

    def invalidate(self): 
        """Destroys the session, both server-side and client-side.
        As a best practice, it should be used when the user logs out of
        the application."""
        self.delete() # remove server-side
        self._delete_cookie = True # remove client-side

    def refresh(self, duration=None, new_session_id=False): # the opposite of invalidate
        """Prolongs the session validity. You can specify for how long passing a
        value in the duration argument (the same rules as for session_age apply).
        Be aware that henceforward this particular session may have different
        expiry date, not respecting the global setting. 

        If new_session_id is True, a new session identifier will be generated.
        This should be used e.g. on user authentication for security reasons."""
        if duration:
            self.duration = duration
            self.expires = self._expires_at()
        else:
            self.expires = self._expires_at()
        if new_session_id:
            self.delete()
            self.session_id = self._generate_session_id()
            self.next_regeneration = self._next_regeneration_at()
        self.dirty = True # force save
        self.save()

    def save(self):
        """Save the session data and metadata to the backend storage
        if necessary (self.dirty == True). On successful save set
        dirty to False."""
        pass

    @staticmethod
    def load(session_id, location):
        """Load the stored session from storage backend or return
        None if the session was not found, in case of stale cookie."""
        pass

    def delete(self):
        """Remove all data representing the session from backend storage."""
        pass

    @staticmethod
    def delete_expired(file_path):
        """Deletes sessions with timestamps in the past form storage."""
        pass

    def serialize(self):
        dump = {'session_id': self.session_id,
                'data': self.data,
                'duration': self.duration,
                'expires': self.expires,
                'ip_address': self.ip_address,
                'user_agent': self.user_agent,
                'security_model': self.security_model,
                'regeneration_interval': self.regeneration_interval,
                'next_regeneration': self.next_regeneration}
        return base64.encodestring(pickle.dumps(dump))

    @staticmethod
    def deserialize(datastring):
        return pickle.loads(base64.decodestring(datastring))


mongo_backend = MongoBackend()
mongo = mongo_backend.get_collection('sessions') 

class MongoDBSession(BaseSession):
    """Class implementing the MongoDB based session storage.
    All sessions are stored in a collection "sessions" in the db
    you specify in the session_storage setting.

    The session document structure is following:
    'session_id': session ID
    'data': serialized session object
    'expires': a timestamp of when the session expires, in sec since epoch
    'user_agent': self-explanatory
    An index on session_id is created automatically, on application's init.

    The end_request() is called after every operation (save, load, delete),
    to return the connection back to the pool.
    """

    def __init__(self, **kwargs):
        super(MongoDBSession, self).__init__(**kwargs)
        
        self.db = mongo # pymongo Collection object - sessions
        if not kwargs.has_key('session_id'):
            self.save()

    def save(self):
        """Upsert a document to the tornado_sessions collection.
        The document's structure is like so:
            {'session_id': self.session_id,
                    'data': self.serialize(),
                    'expires': self._serialize_expires(),
                    'user_agent': self.user_agent}
            """
        # upsert
        self.db.update(
            {'session_id': self.session_id}, # equality criteria
            {'session_id': self.session_id,
             'data': self.serialize(),
             'expires': self._serialize_expires(),
             'user_agent': self.user_agent}, # new document
            upsert=True)
        self.db.database.connection.end_request()
        self.dirty = False

    @staticmethod
    def load(session_id):
        """Load the session from mongo."""
        try:
            data = mongo.find_one({'session_id': session_id})
            if data:
                kwargs = MongoDBSession.deserialize(data['data'])
                mongo.database.connection.end_request()
                return MongoDBSession(**kwargs)
            return None
        except:
            mongo.database.connection.end_request()
            return None

    def delete(self):
        """Remove session from mongo."""
        self.db.remove({'session_id': self.session_id})
        self.db.database.connection.end_request()

    @staticmethod
    def delete_expired(db):
        db.remove({'expires': {'$lte': int(time.time())}})


