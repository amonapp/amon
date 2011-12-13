from amon.core import settings

def logged_in(func):
	def wrapper(self):
		acl = settings.ACL
		if acl == 'True':
			try:
				self.session['user']
			except KeyError:
				self.redirect('/login')
		return func(self)
	return wrapper
