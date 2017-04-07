from django.conf.urls import url

from amon.apps.map import views

urlpatterns = (
    url(r'^$', views.index, name='servers_map'),
)
