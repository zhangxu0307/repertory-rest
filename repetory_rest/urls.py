"""repetory_rest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView, RedirectView

urlpatterns = [


    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('repetory_api.urls')),
    url(r'^api/', include('equipment_api.urls')),
    url(r'^api/', include('part_api.urls')),
    url(r'^api/', include('user_api.urls')),
    url(r'^reset/uid=(?P<uidb64>[0-9A-Za-z_\-]+)&token=(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})$',
            TemplateView.as_view(template_name="password_reset_confirm.html"),
            name='password_reset_confirm'),
    #url(r'^api/', include('forecasting_algorithm.urls')),
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^rest-auth/registration/', include('rest_auth.registration.urls'))
]
