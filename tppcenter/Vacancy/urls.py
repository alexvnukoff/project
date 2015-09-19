from django.conf.urls import patterns, url
from django.contrib import admin

import tppcenter.Vacancy.views
import tppcenter.views

admin.autodiscover()


urlpatterns = patterns('',
     url(r'^$', tppcenter.Vacancy.views.RequirementList.as_view(), name='main'),
     url(r'^page(?P<page>[0-9]+)?/$', tppcenter.Vacancy.views.RequirementList.as_view(), name="paginator"),
     url(r'^my/$', tppcenter.Vacancy.views.RequirementList.as_view(my=True), name='my_main'),
     url(r'^my/page(?P<page>[0-9]+)?/$', tppcenter.Vacancy.views.RequirementList.as_view(my=True), {'my': True}, name="my_main_paginator"),
     url(r'^add/$', tppcenter.Vacancy.views.RequirementCreate.as_view(), name="add"),
     url(r'^update/(?P<pk>[0-9]+)/$', tppcenter.Vacancy.views.RequirementUpdate.as_view(), name="update"),
     url(r'^delete/(?P<pk>[0-9]+)/$', tppcenter.Vacancy.views.RequirementDelete.as_view(), name="delete"),
     url(r'^send/$', tppcenter.Vacancy.views.send_resume,  name="send"),
     url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$', tppcenter.Vacancy.views.RequirementDetail.as_view(), name="detail"),
)
