from django.conf.urls import patterns, include, url
import appl.views
import tppcenter.Tpp.views

import tppcenter.views


from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.Tpp.views.get_tpp_list, name='main'),

     url(r'^page(?P<page>[0-9]+)?/$', tppcenter.Tpp.views.get_tpp_list, name="paginator"),
     url(r'^my/$', tppcenter.Tpp.views.get_tpp_list,{'my':True}, name='my_main'),
     url(r'^my/page(?P<page>[0-9]+)?/$', tppcenter.Tpp.views.get_tpp_list,{'my':True}, name="my_main_paginator"),

     url(r'^add/$', tppcenter.Tpp.views.addTpp, name="add"),
     url(r'^update/([0-9]+)/$', tppcenter.Tpp.views.updateTpp, name="update"),
     url(r'^[a-zA-z-]+-(?P<item_id>[0-9]+)\.html$', tppcenter.Tpp.views.get_tpp_list, name="detail"),

     url(r'^tabs/companies/(?P<tpp>[0-9]+)/$', tppcenter.Tpp.views._tabsCompanies, name="tab_companies"),
     url(r'^tabs/companies/(?P<tpp>[0-9]+)/page(?P<page>[0-9]+)/$', tppcenter.Tpp.views._tabsCompanies, name="tab_companies_paged"),
     url(r'^tabs/news/(?P<tpp>[0-9]+)/$', tppcenter.Tpp.views._tabsNews, name="tab_news"),
     url(r'^tabs/news/(?P<tpp>[0-9]+)/page(?P<page>[0-9]+)/$', tppcenter.Tpp.views._tabsNews, name="tab_news_paged"),
     url(r'^tabs/tenders/(?P<tpp>[0-9]+)/$', tppcenter.Tpp.views._tabsTenders, name="tab_tenders"),
     url(r'^tabs/tenders/(?P<tpp>[0-9]+)/page(?P<page>[0-9]+)/$', tppcenter.Tpp.views._tabsCompanies, name="tab_tenders_paged"),
     url(r'^tabs/exhibitions/(?P<tpp>[0-9]+)/$', tppcenter.Tpp.views._tabsExhibitions, name="tab_exhibitions"),
     url(r'^tabs/exhibitions/(?P<tpp>[0-9]+)/page(?P<page>[0-9]+)/$', tppcenter.Tpp.views._tabsExhibitions, name="tab_exhibitions_paged"),






)