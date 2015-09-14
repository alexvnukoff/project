from django.conf.urls import patterns, url
from django.contrib import admin

import tppcenter.Tenders.views
import tppcenter.views

admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.Tenders.views.TenderList.as_view(), name='main'),
     url(r'^page/(?P<page>[0-9]+)?/$', tppcenter.Tenders.views.TenderList.as_view(), name="paginator"),
     url(r'^my/$', tppcenter.Tenders.views.TenderList.as_view(my=True), name='my_main'),
     url(r'^my/page(?P<page>[0-9]+)?/$', tppcenter.Tenders.views.TenderList.as_view(my=True), name="my_main_paginator"),
     url(r'^add/$', tppcenter.Tenders.views.TenderCreate.as_view(), name="add"),
     url(r'^update/(?P<pk>[0-9]+)/$', tppcenter.Tenders.views.TenderUpdate.as_view(), name="update"),
     url(r'^delete/(?P<item_id>[0-9]+)/$', tppcenter.Tenders.views.tenderForm ,{'action': "delete"}, name="delete"),
     url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$', tppcenter.Tenders.views.TenderDetail.as_view(), name="detail"),
)