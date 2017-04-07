from django.conf.urls import url

from . import views

urlpatterns = (
    url(r'^$', views.view, name='notifications_all'),
    url(r'^(?P<provider_id>\w+)/$', views.edit, name='notifications_edit'),
    url(r'^test/(?P<provider_id>\w+)/$', views.test, name='notifications_test'),
    url(r'^add/(?P<provider_id>\w+)/$', views.add, name='notifications_add'),
    url(r'^edit/(?P<provider_id>\w+)/(?P<notification_id>\w+)/$', views.edit, name='notifications_edit'),
    url(r'^test/(?P<provider_id>\w+)/(?P<notification_id>\w+)/$', views.test, name='notifications_test'),
    url(r'^delete/(?P<provider_id>\w+)/(?P<notification_id>\w+)/$', views.delete, name='notifications_delete'),
)
