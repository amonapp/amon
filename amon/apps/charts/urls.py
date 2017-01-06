from django.conf.urls import patterns, url


urlpatterns = patterns('',
    # AJAX
    url(r'^ajax_localtime_to_unix/$','amon.apps.charts.views.ajax_localtime_to_unix', name='localtime_to_unix'),
    

)