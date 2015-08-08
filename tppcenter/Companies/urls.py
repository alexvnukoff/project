from django.conf.urls import patterns, include, url
import appl.views
import tppcenter.Companies.views

import tppcenter.views


from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.Companies.views.CompanyList.as_view(), name='main'),

     url(r'^page(?P<page>[0-9]+)?/$', tppcenter.Companies.views.CompanyList.as_view(), name="paginator"),
     url(r'^my/$', tppcenter.Companies.views.CompanyList.as_view(my=True), name='my_main'),
     url(r'^my/page(?P<page>[0-9]+)?/$', tppcenter.Companies.views.CompanyList.as_view(my=True), name="my_main_paginator"),
     url(r'^add/$', tppcenter.Companies.views.companyForm,{'action': "add"}, name="add"),
     url(r'^update/(?P<item_id>[0-9]+)/$', tppcenter.Companies.views.companyForm, {'action': "update"}, name="update"),
     url(r'^delete/(?P<item_id>[0-9]+)/$', tppcenter.Companies.views.companyForm, {'action': "delete"}, name="delete"),
     url(r'^(?P<slug>[0-9a-zA-z-]+-(?P<item_id>[0-9]+))\.html$', tppcenter.Companies.views.CompanyDetail.as_view(), name="detail"),
     url(r'^send/$', tppcenter.Companies.views.send_message),



     url(r'^tabs/news/(?P<company>[0-9]+)/$', tppcenter.Companies.views._tab_news, name="tab_news"),
     url(r'^tabs/news/(?P<company>[0-9]+)/page(?P<page>[0-9]+)/$', tppcenter.Companies.views._tab_news, name="tab_news_paged"),
     url(r'^tabs/tenders/(?P<company>[0-9]+)/$', tppcenter.Companies.views._tab_tenders, name="tab_tenders"),
     url(r'^tabs/tenders/(?P<company>[0-9]+)/page(?P<page>[0-9]+)/$', tppcenter.Companies.views._tab_tenders, name="tab_tenders_paged"),
     url(r'^tabs/exhibitions/(?P<company>[0-9]+)/$', tppcenter.Companies.views._tabs_exhibitions, name="tab_exhibitions"),
     url(r'^tabs/exhibitions/(?P<company>[0-9]+)/page(?P<page>[0-9]+)/$', tppcenter.Companies.views._tabs_exhibitions, name="tab_exhibitions_paged"),
     url(r'^tabs/products/(?P<company>[0-9]+)/$', tppcenter.Companies.views._tab_products, name="tab_products"),
     url(r'^tabs/products/(?P<company>[0-9]+)/page(?P<page>[0-9]+)/$', tppcenter.Companies.views._tab_products, name="tab_products_paged"),
     url(r'^tabs/structure/(?P<company>[0-9]+)/$', tppcenter.Companies.views._tab_structure, name="tab_structure"),
     url(r'^tabs/structure/(?P<company>[0-9]+)/page(?P<page>[0-9]+)/$', tppcenter.Companies.views._tab_structure, name="tab_structure_paged"),
     url(r'^tabs/staff/(?P<company>[0-9]+)/$', tppcenter.Companies.views._tab_staff, name="tab_staff"),
     url(r'^tabs/staff/(?P<company>[0-9]+)/page(?P<page>[0-9]+)/$', tppcenter.Companies.views._tab_staff, name="tab_staff_paged"),
     url(r'^tabs/proposal/(?P<company>[0-9]+)/$', tppcenter.Companies.views._tab_proposals, name="tab_proposal"),
     url(r'^tabs/proposal/(?P<company>[0-9]+)/page(?P<page>[0-9]+)/$', tppcenter.Companies.views._tab_proposals, name="tab_proposal_paged"),
     url(r'^tabs/innov/(?P<company>[0-9]+)/$', tppcenter.Companies.views._tab_innovation_projects, name="tab_innov"),
     url(r'^tabs/innov/(?P<company>[0-9]+)/page(?P<page>[0-9]+)/$', tppcenter.Companies.views._tab_innovation_projects, name="tab_innov_paged"),
     url(r'^tabs/gallery/(?P<item>[0-9]+)/$', tppcenter.Companies.views._tab_gallery, name="tabs_gallery"),
     url(r'^tabs/gallery/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$', tppcenter.Companies.views._tab_gallery, name="tabs_gallery_paged"),
     url(r'^tabs/gallery_structure/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$', tppcenter.Companies.views.gallery_structure, name="gallery_structure"),
     url(r'^tabs/gallery/remove/(?P<item>[0-9]+)/$', tppcenter.Companies.views.gallery_remove_item, name="gallery_remove_item"),

)
