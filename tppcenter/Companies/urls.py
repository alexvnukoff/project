from django.conf.urls import patterns, include, url
import appl.views
import tppcenter.Companies.views

import tppcenter.views


from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.Companies.views.get_companies_list, name='main'),

     url(r'^page([0-9]+)?/$', tppcenter.Companies.views.get_companies_list, name="paginator"),
     url(r'^my/$', tppcenter.Companies.views.get_companies_list,{'my': True}, name='my_main'),
     url(r'^my/page(?P<page>[0-9]+)?/$', tppcenter.Companies.views.get_companies_list,{'my':True}, name="my_main_paginator"),
     url(r'^add/$', tppcenter.Companies.views.companyForm,{'action': "add"}, name="add"),
     url(r'^update/(?P<item_id>[0-9]+)/$', tppcenter.Companies.views.companyForm,{'action': "update"}, name="update"),

     url(r'^([0-9a-zA-z-]+-(?P<item_id>[0-9]+))\.html$', tppcenter.Companies.views.get_companies_list, name="detail"),



     url(r'^tabs/news/(?P<company>[0-9]+)/$', tppcenter.Companies.views._tabsNews, name="tab_news"),
     url(r'^tabs/news/(?P<company>[0-9]+)/page(?P<page>[0-9]+)/$', tppcenter.Companies.views._tabsNews, name="tab_news_paged"),
     url(r'^tabs/tenders/(?P<company>[0-9]+)/$', tppcenter.Companies.views._tabsTenders, name="tab_tenders"),
     url(r'^tabs/tenders/(?P<company>[0-9]+)/page(?P<page>[0-9]+)/$', tppcenter.Companies.views._tabsTenders, name="tab_tenders_paged"),
     url(r'^tabs/exhibitions/(?P<company>[0-9]+)/$', tppcenter.Companies.views._tabsExhibitions, name="tab_exhibitions"),
     url(r'^tabs/exhibitions/(?P<company>[0-9]+)/page(?P<page>[0-9]+)/$', tppcenter.Companies.views._tabsExhibitions, name="tab_exhibitions_paged"),
     url(r'^tabs/products/(?P<company>[0-9]+)/$', tppcenter.Companies.views._tabsProducts, name="tab_products"),
     url(r'^tabs/products/(?P<company>[0-9]+)/page(?P<page>[0-9]+)/$', tppcenter.Companies.views._tabsProducts, name="tab_products_paged"),


)
