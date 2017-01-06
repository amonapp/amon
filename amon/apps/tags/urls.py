from django.conf.urls import patterns,url
from django.views.generic import TemplateView


urlpatterns = patterns('amon.apps.tags.views',
    url(r'^$', TemplateView.as_view(template_name="tags/view.html"), name='tags'),
    url(r'^$', TemplateView.as_view(template_name="tags/view.html"), name='view_tags'),
    url(r'^groups/$', TemplateView.as_view(template_name="tags/groups.html"), name='tag_groups'),
)


api_patterns = patterns('amon.apps.tags.api',

    url(
        r'^a/get_tags$',
        'ajax_get_tags',
        name='api_tags_get_tags'
    ), 
    
    # return list of tags for comma separated list url?tags=tag_id, tag_id
    url(
        r'^a/get_tags_list$',
        'ajax_get_tags_list',
        name='api_tags_get_tags_list'
    ), 

    # Tags assigned to servers
    url(
        r'^a/get_server_tags$',
        'ajax_get_only_server_tags',
        name='api_tags_only_server_tags'
    ), 
    # Tags assigned to individual server
    url(
        r'^a/get_tags_for_server/(?P<server_id>\w+)/$',
        'ajax_get_tags_for_server',
        name='api_tags_get_tags_for_server'
    ),

)


urlpatterns = urlpatterns+api_patterns