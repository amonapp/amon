from django import forms


from django.core.urlresolvers import reverse

from amon.apps.files.models import files_model
# from amon.apps.cloudservers.models import (
#     google_integration_model
# )

class LinodeForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.form_data = kwargs.pop('provider_data', None)

        super(LinodeForm, self).__init__(*args, **kwargs)

        try:
            self.fields['name'].initial = self.form_data.get('name')
            self.fields['api_key'].initial = self.form_data.get('api_key')
        except:
            pass

    name = forms.CharField(required=True)
    api_key = forms.CharField(required=True)


class AmazonForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.form_data = kwargs.pop('provider_data', None)

        super(AmazonForm, self).__init__(*args, **kwargs)

        try:
            self.fields['name'].initial = self.form_data.get('name')
            self.fields['access_key'].initial = self.form_data.get('access_key')
            self.fields['secret_key'].initial = self.form_data.get('secret_key')
            self.fields['regions'].initial = self.form_data.get('regions')

            self.fields['regions'].widget.attrs.update({
                'tags-dropdown': '', 
                'data-size': 480,
                'read-only': True,
                'data-tags-url': reverse('api_cloudservers_get_amazon_regions'),
                'data-url': reverse('api_cloudservers_get_amazon_regions'),
            })

        except:
            self.fields['regions'].widget.attrs.update({
                'tags-dropdown': '', 
                'data-size': 480,
                'data-tags-url': reverse('api_cloudservers_get_amazon_regions'),
            })

    name = forms.CharField(required=True)
    access_key = forms.CharField(required=True)
    secret_key = forms.CharField(required=True, widget=forms.PasswordInput(render_value = True))
    regions = forms.CharField(required=True)


class DigitalOceanForm(forms.Form):


    def __init__(self, *args, **kwargs):
        self.form_data = kwargs.pop('provider_data', None)

        super(DigitalOceanForm, self).__init__(*args, **kwargs)

        try:
            self.fields['name'].initial = self.form_data.get('name')
            self.fields['token'].initial = self.form_data.get('token')
        except:
            pass

    name = forms.CharField(required=True)
    token = forms.CharField(required=True)


class GoogleForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        self.form_data = kwargs.pop('provider_data', None)

        super(GoogleForm, self).__init__(*args, **kwargs)

        try:
            self.fields['name'].initial = self.form_data.get('name')
            self.fields['email'].initial = self.form_data.get('email')
            self.fields['project_id'].initial = self.form_data.get('project_id')
            self.fields['json_key'].initial = self.form_data.get('json_key')
        except:
            pass

    name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    project_id = forms.CharField(required=True, label='Project ID')
    json_key = forms.FileField(label='Upload JSON key', required=False)


    def save(self):
        data = self.cleaned_data

        previous_data = google_integration_model.get_by_account_id(self.account_id)
        
        if previous_data:
            previous_file = previous_data.get('file_id')
        else:
            previous_file = None

        json_key_file = data.get('json_key')
        if json_key_file:
            data['file_id'] = files_model.add(json_key_file)
            del data['json_key']

            if previous_file:
                files_model.delete(previous_file)
        
    
        google_integration_model.save(data, account_id=self.account_id)
        





class RackspaceForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.form_data = kwargs.pop('provider_data', None)

        super(RackspaceForm, self).__init__(*args, **kwargs)

        try:
            self.fields['name'].initial = self.form_data.get('name')
            self.fields['username'].initial = self.form_data.get('username')
            self.fields['username'].initial = self.form_data.get('username')
            self.fields['regions'].initial = self.form_data.get('regions')

            self.fields['regions'].widget.attrs.update({
                'tags-dropdown': '', 
                'data-size': 480,
                'read-only': True,
                'data-tags-url': reverse('api_cloudservers_get_rackspace_regions'),
                'data-url': reverse('api_cloudservers_get_rackspace_regions'),
            })

        except:
            self.fields['regions'].widget.attrs.update({
                'tags-dropdown': '', 
                'data-size': 480,
                'data-tags-url': reverse('api_cloudservers_get_rackspace_regions'),
            })

    name = forms.CharField(required=True)        
    api_key = forms.CharField(required=True)
    username = forms.CharField(required=True)
    regions = forms.CharField(required=True)


class VultrForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.form_data = kwargs.pop('provider_data', None)

        super(VultrForm, self).__init__(*args, **kwargs)

        try:
            self.fields['name'].initial = self.form_data.get('name')
            self.fields['api_key'].initial = self.form_data.get('api_key')
        except:
            pass

    name = forms.CharField(required=True)        
    api_key = forms.CharField(required=True)