from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$','amon.apps.dashboards.views.index', name='dashboards'),

    url(r'^create/$', 'amon.apps.dashboards.views.create_dashboard', name='create_dashboard'),
    url(r'^edit/(?P<dashboard_id>\w+)/$', 'amon.apps.dashboards.views.edit_dashboard', name='edit_dashboard'),
    url(r'^reorder/(?P<dashboard_id>\w+)/$', 'amon.apps.dashboards.views.reorder_dashboard', name='reorder_dashboard'),

    url(r'^view/(?P<dashboard_id>\w+)/$', 'amon.apps.dashboards.views.view_dashboard', name='view_dashboard'),
    url(r'^delete/(?P<dashboard_id>\w+)/$', 'amon.apps.dashboards.views.delete_dashboard', name='delete_dashboard'),

    # Ajax
    url(r'^a/edit_dashboard/(?P<dashboard_id>\w+)/$','amon.apps.dashboards.api.edit_dashboard', name='ajax_dashboard_edit'),
    url(r'^a/reorder_metrics/(?P<dashboard_id>\w+)/$','amon.apps.dashboards.api.reorder_metrics', name='ajax_dashboard_reorder_metrics'),
    url(r'^a/add_metric/(?P<dashboard_id>\w+)/$','amon.apps.dashboards.api.add_metric', name='ajax_dashboard_add_metric'),
    url(r'^a/remove_metric/$','amon.apps.dashboards.api.remove_metric', name='ajax_dashboard_remove_metric'),
    url(r'^a/get_all_metrics/(?P<dashboard_id>\w+)/$','amon.apps.dashboards.api.get_all_metrics', name='ajax_dashboard_get_all_metrics'),
    url(r'^a/get_server_metrics/$','amon.apps.dashboards.api.get_server_metrics', name='ajax_dashboard_get_server_metrics'),


    # Metric views
    url(r'^chart/(?P<metric_id>\w+)/$','amon.apps.dashboards.api.dashboard_metric', name='dashboard_metric'),

    # Public
    url(r'^public/charts/(?P<metric_id>\w+)/$','amon.apps.dashboards.api.public_dashboard_metric', name='public_dashboard_metric'),


    url(r'^(?P<account_id>\d+)/(?P<dashboard_id>\w+)/$','amon.apps.dashboards.views.public_dashboard', name='public_dashboard'),

)
