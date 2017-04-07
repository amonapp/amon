from django.conf.urls import url

from amon.apps.install import views

urlpatterns = [
    url(r"^$", views.install_agent, name='install_agent'),
]
