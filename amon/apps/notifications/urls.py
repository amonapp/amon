from django.conf.urls import patterns, url


urlpatterns = patterns('amon.apps.notifications.views',
    url(r'^$', 'view', name='notifications_all'),
    url(r'^(?P<provider_id>\w+)/$', 'edit', name='notifications_edit'),
    url(r'^test/(?P<provider_id>\w+)/$', 'test', name='notifications_test'),
    url(r'^add/(?P<provider_id>\w+)/$', 'add', name='notifications_add'),
    url(r'^edit/(?P<provider_id>\w+)/(?P<notification_id>\w+)/$', 'edit', name='notifications_edit'),
    url(r'^test/(?P<provider_id>\w+)/(?P<notification_id>\w+)/$', 'test', name='notifications_test'),
    url(r'^delete/(?P<provider_id>\w+)/(?P<notification_id>\w+)/$', 'delete', name='notifications_delete'),
)
