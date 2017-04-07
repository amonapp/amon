from django.conf.urls import url

from amon.apps.account.api import (
    UserPreferencesView
)
from amon.apps.account import views

urlpatterns = [
    url(r'^login/$', views.loginview, name='login'),
    url(r'^profile/$', views.view_profile , name='view_profile'),
    url(r'^change_password/$', views.change_password , name='change_password'),
    url(r'^forgotten_password/$', views.forgotten_password , name='forgotten_password'),
    url(r'^reset_password/(?P<token>\w+)$', views.reset_password , name='reset_password'),
    url(r'^create_admin_user/$', views.create_admin_user , name='create_admin_user'),
    url(r'^logout/$', views.logout_user, name='logout'),

    # AJAX
    url(r'^api/update_preferences/$', UserPreferencesView.as_view(), name='api_update_user_preferences'),
]