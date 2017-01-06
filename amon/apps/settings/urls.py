from django.conf.urls import patterns, url

urlpatterns = patterns('amon.apps.settings.views',
    url(r"^$", "data",  name='settings'),
    url(r"^data/$", "data",  name='settings_data'),
    url(r"^smtp/$", "email",  name='settings_email'),
    url(r"^smtp/test/$", "email_test",  name='settings_email_test'),
    url(r"^api/$", "api",  name='settings_api'),
    url(r"^api/delete/(?P<key_id>\w+)/$", "delete_api_key",  name='settings_api_delete_key'),
    url(r"^api/history/$", "api_history",  name='api_history'),

)

