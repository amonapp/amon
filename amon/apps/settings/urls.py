from django.conf.urls import url

from . import views

urlpatterns = (
    url(r"^$", views.data, name='settings'),
    url(r"^data/$", views.data, name='settings_data'),
    url(r"^cleanup/$", views.cleanup, name='settings_cleanup'),
    url(r"^api/$", views.api, name='settings_api'),
    url(r"^api/delete/(?P<key_id>\w+)/$", views.delete_api_key, name='settings_api_delete_key'),
    url(r"^api/history/$", views.api_history, name='api_history'),

)

