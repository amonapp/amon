from django import forms

DURATION_CHOICES = (
    (1800, 'Last 30 minutes'),
    (3600, 'Last 60 minutes'),
    (10800, 'Last 3 hours'),
    (21600, 'Last 6 hours'),
    (43200, 'Last 12 hours'),
    (86400, 'Last 24 hours'),
    (259200, 'Last 3 days'),
    (604800, 'Last 7 days'),
)
     
class DurationForm(forms.Form):
    duration = forms.ChoiceField(choices=DURATION_CHOICES)


SYSTEM_CHARTS = (
    ('all', 'All'),
    ('cpu', 'CPU'),
    ('memory', 'Memory'),
    ('loadavg', 'Load Average'),
    ('network', 'Network'),
    ('disk', 'Disk'),
)



class SystemChartsForm(forms.Form):
    charts = forms.ChoiceField(choices=SYSTEM_CHARTS)


PROCESS_CHARTS = (
    ('cpu', 'CPU'),
    ('memory', 'Memory'),
)

class ProcessChartsForm(forms.Form):
    charts = forms.ChoiceField(choices=PROCESS_CHARTS)