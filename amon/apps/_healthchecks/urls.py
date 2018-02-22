from django.conf.urls import url

from amon.apps.healthchecks import views

urlpatterns = (
    url(r'^$', views.view, name='healthchecks_view'),
    url(r'^delete/(?P<check_id>\w+)/$', views.delete, name='delete_healthcheck'),
)
