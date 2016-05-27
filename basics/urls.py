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
from django.conf.urls import url, include
from django.contrib import admin
from . import views

app_name = 'basics'

urlpatterns = [
    url(r'^$', views.actofgoods_startpage, name='actofgoods_startpage'),
    url(r'^login/$', views.login, name='login'),
    url(r'^register/$', views.register, name='register'),
    url(r'^profil/$', views.profil, name='profil'),
    url(r'^aboutus/$', views.aboutus, name='aboutus'),
    url(r'^privacy/$', views.privacy, name='privacy'),
    url(r'^chat/$', views.chat, name='chat'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^register/$', views.register, name='register'),
    url(r'^home/$', views.home, name='home'),
    url(r'^help/$', views.help, name='help'),
    url(r'^needs_all/$', views.needs_all, name='needs_all'),
    url(r'^needs_new/$', views.needs_new, name='needs_new'),
    url(r'^needs_timeline/$', views.needs_timeline, name='needs_timeline'),
    url(r'^information_all/$', views.information_all, name='information_all'),
    url(r'^information_new/$', views.information_new, name='information_new'),
    url(r'^information_timeline/$', views.information_timeline, name='information_timeline'),
    url(r'^reset_password/$', views.reset_password_page, name='reset_password_page'),
]
