from django.conf.urls import patterns,url


urlpatterns = patterns('amon.apps.bookmarks.views',
    url(
        r'^add$',
        'add',
        name='bookmarks_add'
    ), 

    url(
        r'^delete/(?P<bookmark_id>\w+)$',
        'delete',
        name='bookmarks_delete'
    ), 
)


