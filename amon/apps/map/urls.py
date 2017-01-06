from django.conf.urls import patterns, url

urlpatterns = patterns('amon.apps.map.views',
    url(r'^$', 'index', name='servers_map'),

)
