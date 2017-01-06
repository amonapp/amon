from django import forms
from django.contrib.auth import authenticate
from django.conf import settings
from django.contrib.auth import get_user_model

from amon.apps.notifications.models import notifications_model
from amon.apps.alerts.models import alerts_model
from amon.apps.account.models import user_preferences_model, forgotten_pass_tokens_model
from amon.apps.api.models import api_key_model
from timezone_field import TimeZoneFormField
from amon.apps.account.mailer import send_email_forgotten_password

User = get_user_model()


class LoginForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(render_value=False, attrs={'placeholder': 'Password'}))
    remember_me = forms.BooleanField(widget=forms.CheckboxInput(), label='Remember Me', required=False)

    def clean(self):

        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if user:
                return self.cleaned_data

        raise forms.ValidationError("Invalid login details")


    def clean_remember_me(self):
        remember_me = self.cleaned_data.get('remember_me')

        if not remember_me:
            settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = True
        else:
            settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = False

        return remember_me


class AdminUserForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(render_value=False, attrs={'placeholder': 'Password'}))


    def clean(self):

        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            user = User.objects.filter(email=email).count()
            if user:
                raise forms.ValidationError("User already exists")
        
        return self.cleaned_data

    def save(self):

        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        user = User.objects.create_user(email, password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save()

        notifications_model.save(data={"email": email}, provider_id='email')
        alerts_model.add_initial_data()
        api_key_model.add_initial_data()



class ProfileForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)

        user_preferences = user_preferences_model.get_preferences(user_id=self.user.id)
        user_timezone = user_preferences.get('timezone', 'UTC')

        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['timezone'].widget.attrs.update({'select2-dropdown': '', 'data-size': 360})
        
        self.fields['timezone'].initial = user_timezone
        self.fields['email'].initial = self.user.email
        


    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    timezone = TimeZoneFormField()

        

    # Check email uniqueness
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        if email:
            if self.user.email != email:
                unique = User.objects.filter(email__iexact=email).count()
            
                if unique > 0:
                    raise forms.ValidationError(u'An user with this email address already exists.')
        
        return email


    def save(self):
        data = {'timezone': str(self.cleaned_data['timezone'])}

        user_preferences_model.save_preferences(user_id=self.user.id, data=data)

        self.user.email = self.cleaned_data['email']
        self.user.save()



class ChangePasswordForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ChangePasswordForm, self).__init__(*args, **kwargs)


    current_password = forms.CharField(required=True, widget=(forms.PasswordInput(attrs={'placeholder': 'Password'})))
    new_password = forms.CharField(required=True, widget=(forms.PasswordInput(attrs={'placeholder': 'Password'})))


    def clean_current_password(self):
        password = self.cleaned_data.get('current_password')

        if self.user.check_password(password):
            return self.cleaned_data
        
        raise forms.ValidationError("Your current password is not correct")


    def save(self):
        password = self.cleaned_data.get('new_password')

        self.user.set_password(password)
        self.user.save()


        return True


class ForgottenPasswordForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(ForgottenPasswordForm, self).__init__(*args, **kwargs)


    email = forms.EmailField(required=True, widget=(forms.TextInput(attrs={'placeholder': 'Your Login Email'})))
        
    def clean(self):
        email = self.cleaned_data.get('email')

        if email:
            user = User.objects.filter(email=email).count()
            
            if user == 0:
                raise forms.ValidationError("User does not exists")
        
        return self.cleaned_data



    def save(self):
        email = self.cleaned_data.get('email')

        token = forgotten_pass_tokens_model.set_token(email=email)
        send_email_forgotten_password(token=token, recipients=[email])

        return True


class ResetPasswordForm(forms.Form):
    password = forms.CharField(
        required=True,
        label='Your new password',
        widget=forms.PasswordInput(render_value=False, attrs={'placeholder': 'Password'})
    )
    repeat_password = forms.CharField(
        required=True,
        label='Confirm it',
        widget=forms.PasswordInput(render_value=False, attrs={'placeholder': 'Repeat Password'})
    )


    def clean(self):

        repeat_password = self.cleaned_data.get('repeat_password')
        password = self.cleaned_data.get('password')

        if repeat_password and password:
            if repeat_password != password:
                raise forms.ValidationError("Passwords does not match")
        
        return self.cleaned_data

    def save(self, user=None):
        password = self.cleaned_data.get('password')
        
        user.set_password(password)
        user.save()