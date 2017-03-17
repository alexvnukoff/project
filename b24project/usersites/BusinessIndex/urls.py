# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import include, url
from django.views.generic import TemplateView
from django.utils.translation import ugettext as _
from usersites.views import render_page
from usersites.BusinessIndex.views import BIndexView, BIBranchView

urlpatterns = [
    url(r'^$', BIndexView.as_view(), name='main'),
    url(r'^branch/(?P<pk>[0-9]+)/$', BIBranchView.as_view(), name='branch'),
    url(r'^branch/(?P<pk>[0-9]+)/page(?P<page>[0-9]+)?/$', BIBranchView.as_view(), name="paginator"),
]
