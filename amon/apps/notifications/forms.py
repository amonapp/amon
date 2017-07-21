from django import forms


class BaseNotificationForm(forms.Form):


    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(BaseNotificationForm, self).__init__(*args, **kwargs)


class WebHookForm(BaseNotificationForm):

    def __init__(self, *args, **kwargs):
        self.form_data = kwargs.pop('provider_data', None)

        super(WebHookForm, self).__init__(*args, **kwargs)

        try:
            self.fields['name'].initial = self.form_data.get('name')
            self.fields['url'].initial = self.form_data.get('url')
            self.fields['secret'].initial = self.form_data.get('secret')
        except:
            pass

    name = forms.CharField(required=True)
    url = forms.URLField(required=True, max_length=256, widget=forms.TextInput(attrs={'placeholder': 'URL'}))
    secret = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'A secret string passed in the POST data'}))

class EmailForm(BaseNotificationForm):


    def __init__(self, *args, **kwargs):

        self.form_data = kwargs.pop('provider_data', None)

        super(EmailForm, self).__init__(*args, **kwargs)

        try:
            self.fields['email'].initial = self.form_data.get('email')
        except:
            pass

    email = forms.EmailField()



# Valid values: yellow, green, red, purple, gray, random.
HIPCHAT_COLORS =[('gray','Gray'), ('yellow','Yellow'), ('green','Green'), ('red','Red'), ('purple','Purple')]

class HipChatForm(BaseNotificationForm):

    def __init__(self, *args, **kwargs):

        self.form_data = kwargs.pop('provider_data', None)

        super(HipChatForm, self).__init__(*args, **kwargs)

        try:
            self.fields['name'].initial = self.form_data.get('name')
            self.fields['url'].initial = self.form_data.get('url')
            self.fields['color'].initial = self.form_data.get('color')
        except:
            pass



    name = forms.CharField(required=True)
    url = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Hichat Integration URL'}))
    color = forms.ChoiceField(required=False, choices=HIPCHAT_COLORS, widget=forms.RadioSelect(attrs={'class': 'radiolist'}), initial='gray')

class SlackForm(BaseNotificationForm):

    def __init__(self, *args, **kwargs):
        self.form_data = kwargs.pop('provider_data', None)

        super(SlackForm, self).__init__(*args, **kwargs)

        try:
            self.fields['name'].initial = self.form_data.get('name')
            self.fields['webhook_url'].initial = self.form_data.get('webhook_url')
        except:
            pass

    name = forms.CharField(required=True)
    webhook_url = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Webhook URL'}))

class TelegramForm(BaseNotificationForm):

    def __init__(self, *args, **kwargs):
        self.form_data = kwargs.pop('provider_data', None)

        super(TelegramForm, self).__init__(*args, **kwargs)

        try:
            self.fields['name'].initial = self.form_data.get('name')
            self.fields['token'].initial = self.form_data.get('token')
            self.fields['chat_id'].initial = self.form_data.get('chat_id')
        except:
            pass

    name = forms.CharField(required=True)
    token = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Token'}))
    chat_id = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Chat ID'}))

class PushoverForm(BaseNotificationForm):

    def __init__(self, *args, **kwargs):
        
        self.form_data = kwargs.pop('provider_data', None)

        super(PushoverForm, self).__init__(*args, **kwargs)

        try:
            self.fields['name'].initial = self.form_data.get('name')
            self.fields['user_key'].initial = self.form_data.get('user_key')
            self.fields['application_api_key'].initial = self.form_data.get('application_api_key')
        except:
            pass


    name = forms.CharField(required=True)
    user_key = forms.CharField(required=True, max_length=256, widget=forms.TextInput(attrs={'placeholder': 'User Key'}),
        label='User Key')
    application_api_key = forms.CharField(required=True, label='Application API Key')



class PagerDutyForm(BaseNotificationForm):

    def __init__(self, *args, **kwargs):
        self.form_data = kwargs.pop('provider_data', None)

        super(PagerDutyForm, self).__init__(*args, **kwargs)

        try:
            self.fields['api_key'].initial = self.form_data.get('api_key')
            self.fields['name'].initial = self.form_data.get('name')
            self.fields['incident_key'].initial = self.form_data.get('incident_key')
        except:
            pass

    name = forms.CharField(required=True)
    incident_key = forms.CharField(required=True)
    api_key = forms.CharField(required=True, max_length=256, widget=forms.TextInput(attrs={'placeholder': 'API Key'}))


class OpsGenieForm(BaseNotificationForm):

    def __init__(self, *args, **kwargs):
        self.form_data = kwargs.pop('provider_data', None)

        super(OpsGenieForm, self).__init__(*args, **kwargs)

        try:
            self.fields['name'].initial = self.form_data.get('name')
            self.fields['api_key'].initial = self.form_data.get('api_key')
        except:
            pass

    name = forms.CharField(required=True)
    api_key = forms.CharField(required=True, max_length=256, widget=forms.TextInput(attrs={'placeholder': 'API Key'}))


class VictorOpsForm(BaseNotificationForm):

    def __init__(self, *args, **kwargs):
        self.form_data = kwargs.pop('provider_data', None)

        super(VictorOpsForm, self).__init__(*args, **kwargs)

        try:
            self.fields['name'].initial = self.form_data.get('name')
            self.fields['rest_endpoint'].initial = self.form_data.get('rest_endpoint')
        except:
            pass

    name = forms.CharField(required=True)
    rest_endpoint = forms.URLField(required=True)


