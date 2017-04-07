from django.conf.urls import url

from . import views

urlpatterns = (
    # AJAX
    url(r'^ajax_get_gauge_data_after/$', views.ajax_get_gauge_data_after, name='ajax_get_gauge_data_after'),
    url(r'^view/(?P<server_id>\w+)$', views.view_plugins , name='view_plugins'),
)