from django.conf.urls import patterns, url

urlpatterns = patterns('amon.apps.users.views',

    url(r'^$', 'view_users', name='view_users'),
    url(r'^revoke_access/(?P<user_id>\w+)/$', 'revoke_access', name='users_revoke_access'),
    url(r'^remove_pending/(?P<invitation_id>\w+)/$', 'remove_pending', name='users_remove_pending'),
    url(r'^invite/confirm/(?P<invitation_code>\w+)/$', 'confirm_invite', name='users_confirm_invite'),
)