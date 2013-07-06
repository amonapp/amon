import formencode
from formencode import validators
from amonone.web.apps.auth.models import user_model

class ServerForm(formencode.Schema):
    allow_extra_fields = True
    name = formencode.All(validators.String(not_empty=True, min=4, max=32, strip=True))


class SMTPForm(formencode.Schema):
    allow_extra_fields = True
    address = formencode.All(validators.String(not_empty=True))
    port = formencode.All(validators.Number(not_empty=True))
    from_ = formencode.All(validators.Email(not_empty=True))

class SMSForm(formencode.Schema):
    allow_extra_fields = True
    account = formencode.All(validators.String(not_empty=True))
    token = formencode.All(validators.String(not_empty=True))
    from_ = formencode.All(validators.String(not_empty=True))

class SMSRecepientForm(formencode.Schema):
    name = formencode.All(validators.String(not_empty=True))
    phone = formencode.All(validators.String(not_empty=True))

class EmailRecepientForm(formencode.Schema):
    name = formencode.All(validators.String(not_empty=True))
    email = formencode.All(validators.Email(not_empty=True))

class DataCleanupForm(formencode.Schema):
    server = formencode.All(validators.PlainText(not_empty=True))
    date = formencode.All(validators.DateValidator(not_empty=True))

class AppCleanupForm(formencode.Schema):
    app = formencode.All(validators.PlainText(not_empty=True))
    date = formencode.All(validators.DateValidator(not_empty=True))


class UniqueUsername(formencode.FancyValidator):

	def _to_python(self, value, state):
		user = user_model.username_exists(value)
		if user == 1:
			raise formencode.Invalid('The username already exists', value, state)

		return value

class CreateUserForm(formencode.Schema):
    allow_extra_fields = True
    username = formencode.All(validators.String(not_empty=True, min=4),UniqueUsername())
    password = formencode.All(validators.String(not_empty=True, min=6))

