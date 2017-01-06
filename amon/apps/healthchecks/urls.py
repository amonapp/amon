from django.conf.urls import patterns, url


urlpatterns = patterns('amon.apps.healthchecks.views',
    url(r'^$', 'view', name='healthchecks_view'),
)
