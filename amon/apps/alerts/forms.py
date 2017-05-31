from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse


from amon.apps.servers.models import server_model
from amon.apps.tags.models import tags_model
from amon.apps.alerts.models import alert_mute_servers_model


ABOVE_BELOW_CHOICES = (
    ('above', 'More than'),
    ('below', 'Less than')
)


HEALTCHECKS_STATUS_CHOICES = (
    ('critical', 'CRITICAL'),
    ('warning', 'WARNING')
)

PERIOD_CHOICES = [
    (60, '1 minute'),
    (180, '3 minutes'),
    (300, '5 minutes'),
    (900, '15 minutes'),
    (1800, '30 minutes'), 
    (3600, '1 hour'),
]


MUTE_CHOICES = [
    (1, '1 hour'),
    (2, '2 hours'),
    (4, '4 hours'),
    (8, '8 hours'),
    (0, 'Forever'),
]

PROCESS_CHOICES = [
    ('CPU', 'CPU'),
    ('Memory', 'Memory'),
    ('Down', 'Down'), 
]



if settings.DEBUG == True:
    PERIOD_CHOICES = [(5, '5 seconds'), (30, '30 seconds'), ] + PERIOD_CHOICES

class AlertForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.servers = kwargs.pop('all_servers')

        super(AlertForm, self).__init__(*args, **kwargs)
        
        if self.servers:
            server_fields = [('',''), ('all','All'),]+[(v['_id'],v['name']) for v in self.servers] 
        else:
            server_fields = [('',''),('all','All'),]
        
        self.fields['server'] = forms.ChoiceField(choices=server_fields)
        self.fields['above_below'].widget.attrs.update({'select2-dropdown': '', 'data-size': 120})
        self.fields['server'].widget.attrs.update({
            'server-dropdown': '', 
            'data-placeholder': 'Select server', 
            'data-url': reverse('api_alerts_get_metrics'),
        })
        self.fields['period'].widget.attrs.update({'select2-dropdown': ''})


    metric = forms.CharField(widget=forms.Select())
    command = forms.CharField(required=False)
    metric_value = forms.IntegerField(min_value=0, initial=0)
    above_below = forms.ChoiceField(choices=ABOVE_BELOW_CHOICES)
    period = forms.ChoiceField(choices=PERIOD_CHOICES)

class EditAlertForm(AlertForm):

    def __init__(self, *args, **kwargs):
        super(EditAlertForm, self).__init__(*args, **kwargs)

        if self.servers:
            server_fields = [('',''), ('all','All'),]+[(v['_id'],v['name']) for v in self.servers] 
        else:
            server_fields = [('',''),('all','All'),]

        self.fields['server'] = forms.ChoiceField(choices=server_fields, required=False)
        self.fields['server'].widget.attrs.update({
            'server-dropdown': '', 
        })

    metric = forms.CharField(widget=forms.Select(), required=False)


class MuteForm(forms.Form):


    def __init__(self, *args, **kwargs):
        super(MuteForm, self).__init__(*args, **kwargs)
        all_servers = server_model.get_all()
    
        if all_servers:
            server_fields = [('all','All'),]+[(v['_id'],v['name']) for v in all_servers]
        else:
            server_fields = [('all','All'),]

        self.fields['server'] = forms.ChoiceField(choices=server_fields)
        self.fields['server'].widget.attrs.update({'server-dropdown': '', 'data-size': 250 })


        all_tags = tags_model.get_all()
        if all_tags:
            tags_fields = [(v['_id'],"{0}:{1}".format(v.get('group', {}).get('name'), v['name']) ) for v in all_tags] 

            self.fields['tags'] = forms.MultipleChoiceField(choices=tags_fields, required=False)
            self.fields['tags'].widget.attrs.update({'select2-dropdown': '', 'data-size': 400})

    period = forms.ChoiceField(choices=MUTE_CHOICES, widget=forms.Select(attrs={'select2-dropdown': '', 'data-size': 150}))

    def save(self):
        data = self.cleaned_data
        alert_mute_servers_model.save(data=data)



class HealthCheckAlertForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.servers = kwargs.pop('all_servers')
        super(HealthCheckAlertForm, self).__init__(*args, **kwargs)

        if self.servers:
            server_fields = [('',''), ('all','All'),]+[(v['_id'],v['name']) for v in self.servers] 
        else:
            server_fields = [('',''),('all','All'),]
        
        self.fields['server'] = forms.ChoiceField(choices=server_fields)
        self.fields['server'].widget.attrs.update({
            'server-dropdown': '', 
            'data-placeholder': 'Select server', 
            'data-url': reverse('api_alerts_get_health_check_commands'),
        })
        
    
        self.fields['status'].widget.attrs.update({'select2-dropdown': ''})
        self.fields['period'].widget.attrs.update({'select2-dropdown': ''})

    
    status = forms.ChoiceField(choices=HEALTCHECKS_STATUS_CHOICES)
    period = forms.ChoiceField(choices=PERIOD_CHOICES)


class EditHealthCheckAlertForm(HealthCheckAlertForm):

    def __init__(self, *args, **kwargs):
        super(EditHealthCheckAlertForm, self).__init__(*args, **kwargs)

        if self.servers:
            server_fields = [('',''), ('all','All'),]+[(v['_id'],v['name']) for v in self.servers] 
        else:
            server_fields = [('',''),('all','All'),]

        self.fields['server'] = forms.ChoiceField(choices=server_fields, required=False)
        self.fields['server'].widget.attrs.update({
            'server-dropdown': '', 
        })
        