from django.conf.urls import patterns, include, url
import appl.views
import tppcenter.Tpp.views

import tppcenter.views


from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.Tpp.views.get_tpp_list, name='main'),

     url(r'^page/(?P<page>[0-9]+)?/$', tppcenter.Tpp.views.get_tpp_list, name="paginator"),

     url(r'^add/$', tppcenter.Tpp.views.addTpp, name="add"),
     url(r'^update/([0-9]+)/$', tppcenter.Tpp.views.updateTpp, name="update"),
     url(r'^[a-zA-z-]+-(?P<item_id>[0-9]+).html$', tppcenter.Tpp.views.get_tpp_list, name="detail"),






)