from django.conf.urls import url

from amon.apps.charts import views


urlpatterns = [
    # AJAX
    url(r'^ajax_localtime_to_unix/$',views.ajax_localtime_to_unix, name='localtime_to_unix'),
    

]