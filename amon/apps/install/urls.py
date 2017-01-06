from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r"^$", "amon.apps.install.views.install_agent", name='install_agent'),
    url(r"^config/(?P<server_key>\w+)/$", "amon.apps.install.views.agent_config", name='agent_config'),
    
)

