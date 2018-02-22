from django.conf.urls import url

from amon.apps.servers import views

urlpatterns = (
    url(r'^$', views.all, name='servers'),
    url(r'^add/$', views.add_server, name='add_server'),
    url(r'^edit/(?P<server_id>\w+)/$', views.edit_server, name='edit_server'),
    url(r'^delete/(?P<server_id>\w+)/$', views.delete_server, name='delete_server'),
    url(r'^delete-data/(?P<server_id>\w+)/$', views.delete_data, name='delete_data'),
    url(r'^delete-plugin/(?P<plugin_id>\w+)/server/(?P<server_id>\w+)/$', views.delete_plugin, name='delete_plugin'),
)
