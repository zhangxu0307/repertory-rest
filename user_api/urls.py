from django.conf.urls import url, include
from . import views
from django.views.generic import TemplateView, RedirectView

urlpatterns = [
    url(r'^create_users_info/$', views.CreateUserDeatilInfo.as_view(), name='create_myuser'),
    url(r'^users_display/$', views.UserDisplay.as_view(), name='myuser_display'),
]