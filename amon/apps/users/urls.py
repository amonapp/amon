from django.conf.urls import url

from amon.apps.users import views

# urlpatterns = [
#     url(r'^$', views.view_users, name='view_users'),
#     url(r'^revoke_access/(?P<user_id>\w+)/$', views.revoke_access, name='users_revoke_access'),
#     url(r'^remove_pending/(?P<invitation_id>\w+)/$', views.remove_pending, name='users_remove_pending'),
#     url(r'^invite/confirm/(?P<invitation_code>\w+)/$', views.confirm_invite, name='users_confirm_invite'),
# ]