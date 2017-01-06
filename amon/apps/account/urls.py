from django.conf.urls import patterns, url

from amon.apps.account.api import  (
    UserPreferencesView
)

urlpatterns = patterns('amon.apps.account.views',
    url(r'^login/$','loginview' , name='login'),    
    url(r'^profile/$','view_profile' , name='view_profile'),    
    url(r'^change_password/$','change_password' , name='change_password'),    
    url(r'^forgotten_password/$','forgotten_password' , name='forgotten_password'),    
    url(r'^reset_password/(?P<token>\w+)$','reset_password' , name='reset_password'),    
    url(r'^create_admin_user/$','create_admin_user' , name='create_admin_user'),    
    url(r'^logout/$', 'logout_user', name='logout'),

    url(r'^migrate4to5/$', 'migrate_four_to_five', name='migrate_four_to_five'),

    # AJAX
    url(r'^api/update_preferences/$', UserPreferencesView.as_view(), name='api_update_user_preferences'),
)