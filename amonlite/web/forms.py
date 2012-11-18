import formencode
from formencode import validators
from amon.web.models import user_model

class UniqueUsername(formencode.FancyValidator):

    def _to_python(self, value, state):
        user = user_model.username_exists(value)
        if user == 1:
            raise formencode.Invalid('The username already exists', value, state)

        return value

class CreateUserForm(formencode.Schema):
    username = formencode.All(validators.String(not_empty=True, min=4),UniqueUsername())
    password = validators.String(not_empty=True, min=4)


