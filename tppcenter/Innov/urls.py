from django.conf.urls import patterns, include, url
import appl.views
import tppcenter.Innov.views

import tppcenter.views


from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.Innov.views.get_innov_list, name='main'),

     url(r'^page/(?P<page>[0-9]+)?/$', tppcenter.Innov.views.get_innov_list, name="paginator"),
     url(r'^my/$', tppcenter.Innov.views.get_innov_list,{'my':True}, name='my_main'),
     url(r'^my/page(?P<page>[0-9]+)?/$', tppcenter.Innov.views.get_innov_list,{'my':True}, name="my_main_paginator"),
     url(r'^add/$', tppcenter.Innov.views.innovForm,{'action': 'add'}, name="add"),
     url(r'^update/(?P<item_id>[0-9]+)/$', tppcenter.Innov.views.innovForm,{'action': 'update'} , name="update"),
     url(r'^[a-zA-z0-9-]+-(?P<item_id>[0-9]+).html$', tppcenter.Innov.views.get_innov_list, name="detail"),







)