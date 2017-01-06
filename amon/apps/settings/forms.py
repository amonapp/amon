from django import forms
from django.conf import settings


from amon.apps.notifications.mail.models import email_model
from amon.apps.settings.models import data_retention_model
from amon.apps.api.utils import generate_api_key
from amon.apps.api.models import api_key_model
from amon.apps.settings.emails import send_test_email

class TestSMTPForm(forms.Form):
    send_to = forms.EmailField(required=True, label='Send Email to',
        widget=forms.TextInput(attrs={'placeholder': 'email@example.com'}))


    def save(self):
        send_test_email(to_address=self.cleaned_data['send_to'])


class SMTPForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(SMTPForm, self).__init__(*args, **kwargs)

        email_settings = email_model.get_email_settings()
    
    
        if email_settings:
            for f in self.fields:
                self.fields[f].initial = email_settings.get(f)
            

    host = forms.CharField(required=True)
    port = forms.IntegerField(required=True)
    username = forms.CharField(required=False)
    password = forms.CharField(required=False, widget=forms.PasswordInput())
    sent_from = forms.EmailField(required=True)
    use_tls = forms.BooleanField(widget=forms.CheckboxInput(), label='Use TLS', required=False)


    def save(self):
        email_model.save_email_settings(data=self.cleaned_data)


PERIOD_CHOICES = [
    (1, '24 hours'),
    (15, '15 days'),
    (30, '30 days'), 
    (60, '60 days'), 
    (3600, 'Forever'),
]

CHECK_CHOICES = [
    (15, '15 seconds'), 
    (30, '30 seconds'), 
    (60, '1 minute'),
    (300, '3 minutes'),
    (1800, '5 minutes'), 
]

if settings.DEBUG == True:
    CHECK_CHOICES = [(5, '5 seconds'), ] + CHECK_CHOICES


class DataRetentionForm(forms.Form):


    def __init__(self, *args, **kwargs):

        data_retention_rules = data_retention_model.get_one()

        super(DataRetentionForm, self).__init__(*args, **kwargs)
        self.fields['keep_data'].widget.attrs.update({'select2-dropdown': '', 'data-size': 360})
        self.fields['check_every'].widget.attrs.update({'select2-dropdown': '', 'data-size': 360})

        self.fields['keep_data'].initial = data_retention_rules.get('keep_data', 30)
        self.fields['check_every'].initial = data_retention_rules.get('check_every', 60)
        

    keep_data = forms.TypedChoiceField(choices=PERIOD_CHOICES, label='Keep Data for', coerce=int)
    check_every = forms.TypedChoiceField(choices=CHECK_CHOICES, label='Check every', coerce=int)


    def save(self):
        data_retention_model.delete_all_and_insert(self.cleaned_data)


TRIAL_LOCATIONS = (
    ('send', 'Send'),
    ('full', 'Send and Create'),
)


class ApiKeyForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(ApiKeyForm, self).__init__(*args, **kwargs)
 
    label = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': ''}))

    def save(self):
        label = self.cleaned_data.get('label')
        key = generate_api_key()
        
        data = {'label': label, "key": key, "account_id": settings.ACCOUNT_ID}
        api_key_model.add(data=data)

        
        return True