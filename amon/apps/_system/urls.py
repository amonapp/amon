from django.conf.urls import url

from amon.apps.system import api
from amon.apps.system import views


urlpatterns = (
    # AJAX
    url(r'^a/get_data_after/$', api.ajax_get_data_after, name='ajax_get_data_after'),

    # Views
    url(r'^(?P<server_id>\w+)/$', views.system_view, name='server_system'),
)