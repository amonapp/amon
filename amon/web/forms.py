import formencode
from formencode import validators

class CreateUserForm(formencode.Schema):
     username = validators.String(not_empty=True)
     password = validators.String(not_empty=True)
