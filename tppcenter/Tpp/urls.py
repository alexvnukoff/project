from django.conf.urls import patterns, include, url
import appl.views
import tppcenter.Tpp.views

import tppcenter.views


from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.Tpp.views.ChamberList.as_view(), name='main'),

     url(r'^page(?P<page>[0-9]+)?/$', tppcenter.Tpp.views.ChamberList.as_view(), name="paginator"),
     url(r'^my/$', tppcenter.Tpp.views.ChamberList.as_view(my=True), name='my_main'),
     url(r'^my/page(?P<page>[0-9]+)?/$', tppcenter.Tpp.views.ChamberList.as_view(my=True), name="my_main_paginator"),

     url(r'^add/$', tppcenter.Tpp.views.tpp_form,{'action': 'add'}, name="add"),
     url(r'^update/(?P<item_id>[0-9]+)/$', tppcenter.Tpp.views.tpp_form, {'action': 'update'}, name="update"),

     url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$', tppcenter.Tpp.views.ChamberDetail.as_view(), name="detail"),


     url(r'^tabs/companies/(?P<tpp>[0-9]+)/$', tppcenter.Tpp.views._tab_companies, name="tab_companies"),
     url(r'^tabs/companies/(?P<tpp>[0-9]+)/page(?P<page>[0-9]+)/$', tppcenter.Tpp.views._tab_companies, name="tab_companies_paged"),
     url(r'^tabs/news/(?P<tpp>[0-9]+)/$', tppcenter.Tpp.views._tab_news, name="tab_news"),
     url(r'^tabs/news/(?P<tpp>[0-9]+)/page(?P<page>[0-9]+)/$', tppcenter.Tpp.views._tab_news, name="tab_news_paged"),
     url(r'^tabs/tenders/(?P<tpp>[0-9]+)/$', tppcenter.Tpp.views._tab_tenders, name="tab_tenders"),
     url(r'^tabs/tenders/(?P<tpp>[0-9]+)/page(?P<page>[0-9]+)/$', tppcenter.Tpp.views._tab_companies, name="tab_tenders_paged"),
     url(r'^tabs/exhibitions/(?P<tpp>[0-9]+)/$', tppcenter.Tpp.views._tab_exhibitions, name="tab_exhibitions"),
     url(r'^tabs/exhibitions/(?P<tpp>[0-9]+)/page(?P<page>[0-9]+)/$', tppcenter.Tpp.views._tab_exhibitions, name="tab_exhibitions_paged"),

     url(r'^tabs/innov/(?P<tpp>[0-9]+)/$', tppcenter.Tpp.views._tab_innovation_projects, name="tab_innov"),
     url(r'^tabs/innov/(?P<tpp>[0-9]+)/page(?P<page>[0-9]+)/$', tppcenter.Tpp.views._tab_innovation_projects, name="tab_innov_paged"),
     url(r'^tabs/proposal/(?P<tpp>[0-9]+)/$', tppcenter.Tpp.views._tab_proposals, name="tab_proposal"),
     url(r'^tabs/proposal/(?P<tpp>[0-9]+)/page(?P<page>[0-9]+)/$', tppcenter.Tpp.views._tab_proposals, name="tab_proposal_paged"),

     url(r'^tabs/structure/(?P<tpp>[0-9]+)/$', tppcenter.Tpp.views._tab_structure, name="tab_structure"),
     url(r'^tabs/structure/(?P<tpp>[0-9]+)/page(?P<page>[0-9]+)/$', tppcenter.Tpp.views._tab_structure, name="tab_structure_paged"),
     url(r'^tabs/staff/(?P<tpp>[0-9]+)/$', tppcenter.Tpp.views._tab_staff, name="tab_staff"),
     url(r'^tabs/staff/(?P<tpp>[0-9]+)/page(?P<page>[0-9]+)/$', tppcenter.Tpp.views._tab_staff, name="tab_staff_paged"),
     url(r'^tabs/gallery/(?P<tpp>[0-9]+)/$', tppcenter.Tpp.views._tab_gallery, name="tabs_gallery"),
     url(r'^tabs/gallery/(?P<tpp>[0-9]+)/page(?P<page>[0-9]+)/$', tppcenter.Tpp.views._tab_gallery, name="tabs_gallery_paged"),
     url(r'^tabs/gallery_structure/(?P<tpp>[0-9]+)/page(?P<page>[0-9]+)/$', tppcenter.Tpp.views.gallery_structure, name="gallery_structure"),
     url(r'^tabs/gallery/remove/(?P<tpp>[0-9]+)/$', tppcenter.Tpp.views.gallery_remove_item, name="gallery_remove_item"),
)
