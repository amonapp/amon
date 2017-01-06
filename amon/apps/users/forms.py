import hashlib
import uuid

from django import forms
from annoying.functions import get_object_or_None

from django.contrib.auth import get_user_model


from amon.utils.dates import unix_utc_now
from amon.apps.users.models import invite_model

User = get_user_model()


class InviteForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(InviteForm, self).__init__(*args, **kwargs)


    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Email'}))



    def clean_email(self):
        cleaned_data = self.cleaned_data

        email = cleaned_data['email']

        # Check if invitation already exists
        email_count = invite_model.collection.find({'email': email}).count()

        if email_count > 0:
            raise forms.ValidationError('This user has already been invited.')


        # Ignore invitations for the same email as the logged in user
        if email == self.user.email:
            raise forms.ValidationError("You can't invite yourself.")

        return cleaned_data['email']


    def save(self):
        cleaned_data = self.cleaned_data
        new_invite_email = cleaned_data['email']
        
        data = {
            'email': new_invite_email,
            'invited_by': self.user.id,
            'sent': unix_utc_now()
        }
        

        invitation_code_string = "{0}{1}{2}".format(self.user.id, new_invite_email , unix_utc_now())
        data['invitation_code'] = hashlib.sha224(invitation_code_string).hexdigest()

        invite_model.create_invitation(data=data)

        return data
    

    


class InviteNewUserForm(forms.Form):
    password = forms.CharField(required=True, widget=(forms.PasswordInput(attrs={'placeholder': 'Password'})))

    def __init__(self, *args, **kwargs):
        self.invite = kwargs.pop('invite', None)
        super(InviteNewUserForm, self).__init__(*args, **kwargs)

    

    def clean_password(self):
        password = self.cleaned_data.get('password', None)
    
        if len(password) < 6:
            raise forms.ValidationError('Your password has to be at least 6 charactes')

        return self.cleaned_data['password']


    def save(self):

        password = self.cleaned_data.get('password')
        email = self.invite.get('email')
        username = uuid.uuid4().hex[:30]
        
        user = User.create_user(username, password, email=email)
        user.is_admin = False
        user.is_staff = False
        user.is_superuser = False
        user.save()

        invite_model.delete(self.invite['_id'])
        
        return user