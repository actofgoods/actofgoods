"""actofgoods URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
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
from django.conf.urls import url, include, handler403, handler404
from django.contrib import admin

handler400 = 'basics.views.bad_request'
handler403 = 'basics.views.permission_denied'
handler404 = 'basics.views.page_not_found'
handler500 = 'basics.views.server_error'

urlpatterns = [
    url(r'^', include('basics.urls')),
    url(r'^', include('administration.urls')),

]
