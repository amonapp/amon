from amonone.web.apps.core.baseview import BaseView
from amonone.web.apps.auth.forms import CreateUserForm
from amonone.web.apps.auth.models import user_model
from formencode.validators import Invalid as InvalidForm


class LoginView(BaseView):

    def initialize(self):
        super(LoginView, self).initialize()


    def get(self):

        # Redirect if there are no users in the database
        users = user_model.count_users()
        if users == 0:
            self.redirect('/create_user')
        else:
            message =  self.session.get('message',None)
            errors =  self.session.get('errors',None)
            next = self.get_argument('next', None)

            try:
                del self.session['errors']
                del self.session['message']
            except:
                pass

            self.render('auth/login.html', message=message, errors=errors, next=next)


    def post(self):
        form_data = {
                "username": self.get_argument('username', ''),
                "password": self.get_argument('password', ''),
                }

        user = user_model.check_user(form_data)

        if len(user) == 0:
            self.session['errors'] = "Invalid login details"
            self.redirect('/login')
        else:
            apps = user.get('apps',None)
            servers = user.get('servers', None)
            self.session['user'] = {'username': user['username'],
                    'user_id': user['_id'], 'type': user['type'],
                    'apps': apps, 'servers': servers}

            next = self.get_argument('next', None)
            redirect = next if next != None else "/"
            
            self.redirect(redirect)

class LogoutView(BaseView):

    def initialize(self):
        super(LogoutView, self).initialize()


    def get(self):

        if self.acl == 'False':
            self.redirect('/')
        else:
            try:
                del self.session['user']
            except:
                pass

            self.redirect('/login')

class CreateInitialUserView(BaseView):

    def initialize(self):
        super(CreateInitialUserView, self).initialize()


    def get(self):

        errors = self.session.get('errors', None)
        form_data = self.session.get('form_data', None)

        # This page is active only when acl is enabled
        if self.acl == 'False':
            self.redirect('/')
        else:
            # This page is active only when there are no users in the system
            users = user_model.count_users()

            if users == 0:
                self.render('auth/create_user.html', errors=errors, form_data=form_data)
            else:
                self.redirect('/login')


    def post(self):
        form_data = {
                "username": self.get_argument('username', ''),
                "password": self.get_argument('password',''),
                "type": "admin",
                "servers": [],
                "apps": []
                }
        try:
            valid_data = CreateUserForm.to_python(form_data)
            user_model.create_user(valid_data)
            self.session['message'] = 'User successfuly created. You can now log in'

            try:
                del self.session['errors']
                del self.session['form_data']
            except:
                pass

            self.redirect('/login')

        except InvalidForm, e:
            self.session['errors'] = e.unpack_errors()
            self.session['form_data'] = form_data

            self.redirect('/create_user')




