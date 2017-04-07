from django.conf.urls import url

from amon.apps.bookmarks import views

urlpatterns = [
    url(
        r'^add$',
        views.add,
        name='bookmarks_add'
    ), 

    url(
        r'^delete/(?P<bookmark_id>\w+)$',
        views.delete,
        name='bookmarks_delete'
    ), 
]


