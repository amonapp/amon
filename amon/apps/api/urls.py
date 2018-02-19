from django.conf.urls import url

from rest_framework.documentation import include_docs_urls

urlpatterns = [
    url(r'^docs/', include_docs_urls(
        title='Amon API Docs',
        authentication_classes=[],
        permission_classes=[]))
]


# from amon.apps.api.views.core import (
#     SystemDataView,
#     LegacySystemDataView,
#     SystemInfoView,
#     TestView,
#     CheckIpAddressView
# )
# from amon.apps.api.views.telegraf import TelegrafDataView
# from amon.apps.api.views.collectd import CollectdDataView


# from amon.apps.api.views.servers import (
#     ServersListView,
#     ServersCreateView,
#     ServersDeleteView
# )

# from amon.apps.api.views.tags import (
#     TagsListView,
#     TagsCreateView,
#     TagsDeleteView,
#     TagsUpdateView,
#     TagGroupsListView,
#     TagGroupsCreateView,
#     TagGroupsDeleteView,
#     TagGroupsUpdateView
# )

# from amon.apps.api.views.alerts import (
#     AlertsListView,
#     AlertsMuteView,
#     AlertsMuteAllView,
#     AlertsUnMuteAllView
# )


# urlpatterns = [
    # url(r'^test/(?P<server_key>\w+)$', TestView.as_view(), name='api_test'),
    # url(r'^checkip$', CheckIpAddressView.as_view(), name='check_ip'),
    # url(r'^collectd/(?P<server_key>\w+)$', CollectdDataView.as_view(), name='api_collectd'),
    # url(r'^system/(?P<server_key>\w+)$', LegacySystemDataView.as_view(), name='api_system_legacy'),
    # url(r'^info/(?P<server_key>\w+)$', SystemInfoView.as_view(), name='api_system_info'),
    # url(r'^telegraf/(?P<server_key>\w+)$', TelegrafDataView.as_view(), name='api_telegraf'),

    # url(r'^system/v2/$', SystemDataView.as_view(), name='api_system'),
# ]

# server_urls = [
#     url(r'^v1/servers/list/$', ServersListView.as_view(), name='api_servers_list'),
#     url(r'^v1/servers/create/$', ServersCreateView.as_view(), name='api_servers_create'),
#     url(r'^v1/servers/delete/(?P<server_id>\w+)/$', ServersDeleteView.as_view(), name='api_servers_delete'),
# ]

# alerts_urls = [
#     url(r'^v1/alerts/list/$', AlertsListView.as_view(), name='api_alerts_list'),
#     url(r'^v1/alerts/mute/all/$', AlertsMuteAllView.as_view(), name='api_alerts_mute_all'),
#     url(r'^v1/alerts/unmute/all/$', AlertsUnMuteAllView.as_view(), name='api_alerts_unmute_all'),
#     url(r'^v1/alerts/mute/(?P<alert_id>\w+)/$', AlertsMuteView.as_view(), name='api_alerts_mute'),
#     url(r'^v1/alerts/delete/(?P<alert_id>\w+)/$', AlertsMuteView.as_view(), name='api_alerts_delete'),
# ]





# urlpatterns += server_urls
# urlpatterns += alerts_urls
