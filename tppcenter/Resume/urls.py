from django.conf.urls import patterns, include, url
import appl.views
import tppcenter.Resume.views

import tppcenter.views


from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.Resume.views.ResumeList.as_view(), name='main'),
     url(r'^page/(?P<page>[0-9]+)?/$', tppcenter.Resume.views.ResumeList.as_view(), name="paginator"),
     url(r'^my/$', tppcenter.Resume.views.ResumeList.as_view(my=True), name='my_main'),
     url(r'^my/page(?P<page>[0-9]+)?/$', tppcenter.Resume.views.ResumeList.as_view(my=True), name="my_main_paginator"),



     url(r'^add/$', tppcenter.Resume.views.resumeForm,{'action': 'add'} , name="add"),
     url(r'^update/(?P<item_id>[0-9]+)/$', tppcenter.Resume.views.resumeForm,{'action': 'update'}, name="update"),
     url(r'^delete/(?P<item_id>[0-9]+)/$', tppcenter.Resume.views.resumeForm ,{'action': "delete"}, name="delete"),
     url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$', tppcenter.Resume.views.ResumeDetail.as_view(), name="detail"),






)