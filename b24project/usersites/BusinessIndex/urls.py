# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import include, url
from django.views.generic import TemplateView
from django.utils.translation import ugettext as _
from usersites.views import render_page
from usersites.BusinessIndex import views

urlpatterns = [
    url(r'^$', views.BIndexView.as_view(), name='main'),
    url(r'^branch/(?P<pk>[0-9]+)/detail/$', views.BIBranchView.as_view(), name='branch'),
]
