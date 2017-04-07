from django.conf.urls import url

from amon.apps.healthchecks import views

urlpatterns = (
    url(r'^$', views.view, name='healthchecks_view'),
)
