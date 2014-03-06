from django.conf.urls import patterns, include, url
import appl.views
import tppcenter.Exhibitions.views

import tppcenter.views


from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.Exhibitions.views.get_exhibitions_list, name='main'),

     url(r'^page/(?P<page>[0-9]+)?/$', tppcenter.Exhibitions.views.get_exhibitions_list, name="paginator"),
     url(r'^add/$', tppcenter.Exhibitions.views.addExhibition, name="add"),
     url(r'^my/$', tppcenter.Exhibitions.views.get_exhibitions_list,{'my':True}, name='my_main'),
     url(r'^my/page(?P<page>[0-9]+)?/$', tppcenter.Exhibitions.views.get_exhibitions_list,{'my':True}, name="my_main_paginator"),
     url(r'^update/([0-9]+)/$', tppcenter.Exhibitions.views.updateExhibition, name="update"),
     url(r'^[a-zA-z0-9-]+-(?P<item_id>[0-9]+).html$', tppcenter.Exhibitions.views.get_exhibitions_list, name="detail"),






)