from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r"^$", "amon.apps.install.views.install_agent", name='install_agent'),
)

