from django.conf.urls import include, url
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^$', RedirectView.as_view(pattern_name='login')),
    url(r'^install/', include('amon.apps.install.urls')),
    url(r'^account/', include('amon.apps.account.urls')),
    url(r'^api/', include('amon.apps.api.urls')),
    
    # App
    url(r'^cloud-servers/', include('amon.apps.cloudservers.urls')),
    url(r"^servers/", include('amon.apps.servers.urls')),
    url(r"^servers/map/", include('amon.apps.map.urls')),
    url(r"^checks/", include('amon.apps.healthchecks.urls')),
    url(r"^system/", include('amon.apps.system.urls')),
    url(r"^processes/", include('amon.apps.processes.urls')),
    url(r"^alerts/", include('amon.apps.alerts.urls')),
    url(r"^plugins/", include('amon.apps.plugins.urls')),
    url(r"^charts/", include('amon.apps.charts.urls')),
    url(r"^dashboards/", include('amon.apps.dashboards.urls')),
    url(r"^settings/", include('amon.apps.settings.urls')),

    url(r"^settings/notifications/", include('amon.apps.notifications.urls')),
    url(r"^tags/", include('amon.apps.tags.urls')),
    url(r"^bookmarks/", include('amon.apps.bookmarks.urls')),
    url(r"^users/", include('amon.apps.users.urls')),
]
