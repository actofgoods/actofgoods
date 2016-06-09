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

app_name = 'administration'

urlpatterns = [
    url(r'^administration/mails/$', views.mails, name='mails'),
    url(r'^administration/categories/$', views.categories, name='categories'),
    url(r'^administration/needs/$', views.needs, name='needs'),
    url(r'^administration/informations/$', views.informations, name='informations'),
    url(r'^administration/users/$', views.users, name='users'),
    url(r'^administration/groups/$', views.groups, name='groups'),
    url(r'^administration/new_group/$', views.new_group, name='new_group'),
    url(r'^administration/users/(?P<pk>\d+)/delete/$', views.user_delete, name='user_delete'),
    url(r'^administration/groups/(?P<pk>\d+)/delete/$', views.group_delete, name='group_delete'),
    
]
