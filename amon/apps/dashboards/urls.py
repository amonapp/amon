from django.conf.urls import url

from amon.apps.dashboards import views
from amon.apps.dashboards import api

urlpatterns = (
    url(r'^$', views.index, name='dashboards'),

    url(r'^create/$', views.create_dashboard, name='create_dashboard'),
    url(r'^edit/(?P<dashboard_id>\w+)/$', views.edit_dashboard, name='edit_dashboard'),
    url(r'^reorder/(?P<dashboard_id>\w+)/$', views.reorder_dashboard, name='reorder_dashboard'),

    url(r'^view/(?P<dashboard_id>\w+)/$', views.view_dashboard, name='view_dashboard'),
    url(r'^delete/(?P<dashboard_id>\w+)/$', views.delete_dashboard, name='delete_dashboard'),

    # Ajax
    url(r'^a/edit_dashboard/(?P<dashboard_id>\w+)/$', api.edit_dashboard, name='ajax_dashboard_edit'),
    url(r'^a/reorder_metrics/(?P<dashboard_id>\w+)/$', api.reorder_metrics, name='ajax_dashboard_reorder_metrics'),
    url(r'^a/add_metric/(?P<dashboard_id>\w+)/$', api.add_metric, name='ajax_dashboard_add_metric'),
    url(r'^a/remove_metric/$', api.remove_metric, name='ajax_dashboard_remove_metric'),
    url(r'^a/get_all_metrics/(?P<dashboard_id>\w+)/$', api.get_all_metrics, name='ajax_dashboard_get_all_metrics'),
    url(r'^a/get_server_metrics/$', api.get_server_metrics, name='ajax_dashboard_get_server_metrics'),


    # Metric views
    url(r'^chart/(?P<metric_id>\w+)/$', api.dashboard_metric, name='dashboard_metric'),

    # Public
    url(r'^public/charts/(?P<metric_id>\w+)/$', api.public_dashboard_metric, name='public_dashboard_metric'),


    url(r'^(?P<account_id>\w+)/(?P<dashboard_id>\w+)/$', views.public_dashboard, name='public_dashboard'),

)
