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
    url(r'^administration/requests/$', views.requests, name='requests'),
    url(r'^administration/categories/$', views.categories, name='categories'),
    url(r'^administration/needs/$', views.needs, name='needs'),
    url(r'^administration/informations/$', views.informations, name='informations'),
    url(r'^administration/users/$', views.users, name='users'),
    url(r'^administration/groups/$', views.groups, name='groups'),
    url(r'^administration/users/(?P<pk>\d+)/delete/$', views.user_delete, name='user_delete'),
    url(r'^administration/groups/(?P<pk>\d+)/delete/$', views.group_delete, name='group_delete'),
    url(r'^administration/needs/delete/$', views.need_delete, name='need_delete'),
    url(r'^administration/informations/(?P<pk>\d+)/delete/$', views.information_delete, name='information_delete'),
    url(r'^administration/users/(?P<pk>\d+)/make_admin/$', views.make_admin, name='make_admin'),
    url(r'^administration/categories/(?P<pk>\d+)/delete/$', views.categories_delete, name='categories_delete'),
    url(r'^administration/work_on_request/$', views.work_on_request, name='work_on_request'),
    url(r'^administration/request_done/$', views.request_done, name='request_done'),
    
]
