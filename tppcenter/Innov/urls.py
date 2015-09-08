from django.conf.urls import patterns, url
from django.contrib import admin

import tppcenter.Innov.views
import tppcenter.views

admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.Innov.views.InnovationProjectList.as_view(), name='main'),

     url(r'^page(?P<page>[0-9]+)?/$', tppcenter.Innov.views.InnovationProjectList.as_view(), name="paginator"),
     url(r'^my/$', tppcenter.Innov.views.InnovationProjectList.as_view(my=True), name='my_main'),
     url(r'^my/page(?P<page>[0-9]+)?/$', tppcenter.Innov.views.InnovationProjectList.as_view(my=True), name="my_main_paginator"),
     url(r'^add/$', tppcenter.Innov.views.InnovationProjectCreate.as_view(), name="add"),
     url(r'^update/(?P<pk>[0-9]+)/$', tppcenter.Innov.views.InnovationProjectUpdate.as_view(), name="update"),
     url(r'^delete/(?P<item_id>[0-9]+)/$', tppcenter.Innov.views.innovForm, {'action': 'delete'}, name="delete"),
     url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$', tppcenter.Innov.views.InnovationProjectDetail.as_view(), name="detail"),







)
