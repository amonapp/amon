from django import forms
from django.conf import settings

from amon.apps.settings.forms import DataRetentionForm
from amon.apps.servers.models import server_model
from amon.apps.tags.models import tags_model
from django.urls import reverse





class ServerForm(DataRetentionForm):

    tags = forms.CharField(max_length=256, required=False)
    name = forms.CharField(max_length=256, widget=forms.TextInput(attrs={'placeholder': 'Server name'}))

    def __init__(self, *args, **kwargs):
        self.server = kwargs.pop('server', None)
        super(ServerForm, self).__init__(*args, **kwargs)

        if self.server:
            tags = self.server.get('tags', [])
            self.fields['name'].initial = self.server.get('name', "")
            self.fields['tags'].initial = ",".join(map(str, tags))
            self.fields['keep_data'].initial = self.server.get('keep_data', 30)
            self.fields['check_every'].initial = self.server.get('check_every', 60)

            self.fields['tags'].widget.attrs.update({
                'tags-dropdown': '', 'data-size': 360,
                'data-tags-url': reverse('api_tags_get_tags'),
                'data-url': reverse('api_tags_get_tags_for_server', kwargs={'server_id': self.server['_id']}),
            })

        else:
            self.fields['tags'].widget.attrs.update({
                'tags-dropdown': '', 'data-size': 360,
                'data-tags-url': reverse('api_tags_get_tags'),
            })

    def save(self):
        data = self.cleaned_data

        tags = data.get('tags', [])
        if len(tags) > 0:
            data['tags'] = tags_model.get_tags_ids(tags_string=tags)

        # Update
        if self.server:
            server_model.update(data, self.server['_id'])

        # Create
        else:
            server_key = server_model.add(
                data.get('name'),
                account_id=settings.ACCOUNT_ID,
                keep_data=data.get('keep_data'),
                check_every=data.get('check_every'),
                tags=data['tags']
            )

            server = server_model.get_server_by_key(server_key)

            return server
    
    

