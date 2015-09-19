from django.conf.urls import patterns, url
from django.contrib import admin

import tppcenter.Tenders.views
import tppcenter.views

admin.autodiscover()


urlpatterns = patterns('',
     url(r'^$', tppcenter.Tenders.views.TenderList.as_view(), name='main'),
     url(r'^page/(?P<page>[0-9]+)?/$', tppcenter.Tenders.views.TenderList.as_view(), name="paginator"),
     url(r'^my/$', tppcenter.Tenders.views.TenderList.as_view(my=True), name='my_main'),
     url(r'^my/page(?P<page>[0-9]+)?/$', tppcenter.Tenders.views.TenderList.as_view(my=True), name="my_main_paginator"),
     url(r'^add/$', tppcenter.Tenders.views.TenderCreate.as_view(), name="add"),
     url(r'^update/(?P<pk>[0-9]+)/$', tppcenter.Tenders.views.TenderUpdate.as_view(), name="update"),
     url(r'^delete/(?P<pk>[0-9]+)/$', tppcenter.Tenders.views.TenderDelete.as_view(), name="delete"),
     url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$', tppcenter.Tenders.views.TenderDetail.as_view(), name="detail"),

     url(r'^tabs/gallery/(?P<item>[0-9]+)/$', tppcenter.Tenders.views.TenderGalleryImageList.as_view(), name="tabs_gallery"),
     url(r'^tabs/gallery/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$', tppcenter.Tenders.views.TenderGalleryImageList.as_view(), name="tabs_gallery_paged"),
     url(r'^tabs/gallery_structure/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$', tppcenter.Tenders.views.TenderGalleryImageList.as_view(is_structure=True), name="gallery_structure"),
     url(r'^tabs/gallery/(?P<item>[0-9]+)/remove/(?P<pk>[0-9]+)/$', tppcenter.Tenders.views.DeleteTenderGalleryImage.as_view(), name="gallery_remove_item"),

     url(r'^tabs/documents/(?P<item>[0-9]+)/$', tppcenter.Tenders.views.TenderDocumentList.as_view(), name="tabs_documents"),
     url(r'^tabs/documents/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$', tppcenter.Tenders.views.TenderDocumentList.as_view(), name="tabs_documents_paged"),
     url(r'^tabs/documents_structure/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$', tppcenter.Tenders.views.TenderDocumentList.as_view(is_structure=True), name="documents_structure"),
     url(r'^tabs/documents/(?P<item>[0-9]+)/remove/(?P<pk>[0-9]+)/$', tppcenter.Tenders.views.DeleteTenderDocument.as_view(), name="documents_remove_item"),
)
