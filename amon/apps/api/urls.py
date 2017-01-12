from django.conf.urls import patterns, url
from amon.apps.api.views.core import (
    SystemDataView,
    LegacySystemDataView,
    SystemInfoView,
    TestView,
    CheckIpAddressView
)
from amon.apps.api.views.telegraf import TelegrafDataView
from amon.apps.api.views.collectd import CollectdDataView

from amon.apps.api.views.servers import (
    ServersListView,
    ServersCreateView,
    ServersDeleteView
)

from amon.apps.api.views.tags import (
    TagsListView,
    TagsCreateView,
    TagsDeleteView,
    TagsUpdateView,
    TagGroupsListView,
    TagGroupsCreateView,
    TagGroupsDeleteView,
    TagGroupsUpdateView
)

from amon.apps.api.views.alerts import (
    AlertsListView,
    AlertsMuteView,
    AlertsMuteAllView,
    AlertsUnMuteAllView
)


from amon.apps.api.views.cloudservers import (
    CloudServersSyncView,
    CloudServersGetServerKeyView
)

urlpatterns = patterns('',
    url(r'^test/(?P<server_key>\w+)$', TestView.as_view(), name='api_test'),
    url(r'^checkip$', CheckIpAddressView.as_view(), name='check_ip'),
    url(r'^collectd/(?P<server_key>\w+)$', CollectdDataView.as_view(), name='api_collectd'),
    url(r'^system/(?P<server_key>\w+)$', LegacySystemDataView.as_view(), name='api_system_legacy'),
    url(r'^info/(?P<server_key>\w+)$', SystemInfoView.as_view(), name='api_system_info'),
    url(r'^telegraf/(?P<server_key>\w+)$', TelegrafDataView.as_view(), name='api_telegraf'),

    url(r'^system/v2/$', SystemDataView.as_view(), name='api_system'),
)

server_urls = patterns('',
    url(r'^v1/servers/list/$', ServersListView.as_view(), name='api_servers_list'),
    url(r'^v1/servers/create/$', ServersCreateView.as_view(), name='api_servers_create'),
    url(r'^v1/servers/delete/(?P<server_id>\w+)/$', ServersDeleteView.as_view(), name='api_servers_delete'),
)

alerts_urls = patterns('',
    url(r'^v1/alerts/list/$', AlertsListView.as_view(), name='api_alerts_list'),
    url(r'^v1/alerts/mute/all/$', AlertsMuteAllView.as_view(), name='api_alerts_mute_all'),
    url(r'^v1/alerts/unmute/all/$', AlertsUnMuteAllView.as_view(), name='api_alerts_unmute_all'),
    url(r'^v1/alerts/mute/(?P<alert_id>\w+)/$', AlertsMuteView.as_view(), name='api_alerts_mute'),
    url(r'^v1/alerts/delete/(?P<alert_id>\w+)/$', AlertsMuteView.as_view(), name='api_alerts_delete'),
)


cloudserver_urls = patterns('',
    url(r'^v1/cloudservers/sync/(?P<provider_id>\w+)/$', CloudServersSyncView.as_view(), name='api_cloudservers_sync'),
    url(r'^v1/cloudservers/get-server-key/(?P<provider_id>\w+)/$', CloudServersGetServerKeyView.as_view(), name='api_cloudservers_get_server_key'),
)

tags_urls = patterns('',
    url(r'^v1/tags/list/$', TagsListView.as_view(), name='api_tags_list'),
    url(r'^v1/tags/create/$', TagsCreateView.as_view(), name='api_tags_create'),
    url(r'^v1/tags/update/$', TagsUpdateView.as_view(), name='api_tags_update'),
    url(r'^v1/tags/delete/$', TagsDeleteView.as_view(), name='api_tags_delete'),
    url(r'^v1/tags/groups/list/$', TagGroupsListView.as_view(), name='api_tag_groups_list'),
    url(r'^v1/tags/groups/create/$', TagGroupsCreateView.as_view(), name='api_tag_groups_create'),
    url(r'^v1/tags/groups/update/$', TagGroupsUpdateView.as_view(), name='api_tag_groups_update'),
    url(r'^v1/tags/groups/delete/$', TagGroupsDeleteView.as_view(), name='api_tag_groups_delete'),
)


urlpatterns += server_urls
urlpatterns += alerts_urls
urlpatterns += cloudserver_urls
urlpatterns += tags_urls
