from django.conf.urls import url

from b24online.Tpp.views import ChamberList, ChamberCreate, _tab_companies, ChamberUpdate, ChamberDetail, _tab_news, \
    _tab_exhibitions, _tab_tenders, _tab_innovation_projects, _tab_proposals, _tab_structure, _tab_staff, \
    ChamberGalleryImageList, DeleteChamberGalleryImage, ChamberDocumentList, DeleteChamberDocument

urlpatterns = [
    url(r'^$', ChamberList.as_view(), name='main'),

    url(r'^page(?P<page>[0-9]+)?/$', ChamberList.as_view(), name="paginator"),
    url(r'^my/$', ChamberList.as_view(my=True), name='my_main'),
    url(r'^my/page(?P<page>[0-9]+)?/$', ChamberList.as_view(my=True), name="my_main_paginator"),
    url(r'^add/$', ChamberCreate.as_view(), name="add"),
    url(r'^update/(?P<pk>[0-9]+)/$', ChamberUpdate.as_view(), name="update"),
    url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$', ChamberDetail.as_view(), name="detail"),

    url(r'^tabs/companies/(?P<tpp>[0-9]+)/$', _tab_companies, name="tab_companies"),
    url(r'^tabs/companies/(?P<tpp>[0-9]+)/page(?P<page>[0-9]+)/$', _tab_companies, name="tab_companies_paged"),
    url(r'^tabs/news/(?P<tpp>[0-9]+)/$', _tab_news, name="tab_news"),
    url(r'^tabs/news/(?P<tpp>[0-9]+)/page(?P<page>[0-9]+)/$', _tab_news, name="tab_news_paged"),
    url(r'^tabs/tenders/(?P<tpp>[0-9]+)/$', _tab_tenders, name="tab_tenders"),
    url(r'^tabs/tenders/(?P<tpp>[0-9]+)/page(?P<page>[0-9]+)/$', _tab_companies, name="tab_tenders_paged"),
    url(r'^tabs/exhibitions/(?P<tpp>[0-9]+)/$', _tab_exhibitions, name="tab_exhibitions"),
    url(r'^tabs/exhibitions/(?P<tpp>[0-9]+)/page(?P<page>[0-9]+)/$', _tab_exhibitions, name="tab_exhibitions_paged"),
    url(r'^tabs/innov/(?P<tpp>[0-9]+)/$', _tab_innovation_projects, name="tab_innov"),
    url(r'^tabs/innov/(?P<tpp>[0-9]+)/page(?P<page>[0-9]+)/$', _tab_innovation_projects, name="tab_innov_paged"),
    url(r'^tabs/proposal/(?P<tpp>[0-9]+)/$', _tab_proposals, name="tab_proposal"),
    url(r'^tabs/proposal/(?P<tpp>[0-9]+)/page(?P<page>[0-9]+)/$', _tab_proposals, name="tab_proposal_paged"),
    url(r'^tabs/structure/(?P<tpp>[0-9]+)/$', _tab_structure, name="tab_structure"),
    url(r'^tabs/structure/(?P<tpp>[0-9]+)/page(?P<page>[0-9]+)/$', _tab_structure, name="tab_structure_paged"),
    url(r'^tabs/staff/(?P<tpp>[0-9]+)/$', _tab_staff, name="tab_staff"),
    url(r'^tabs/staff/(?P<tpp>[0-9]+)/page(?P<page>[0-9]+)/$', _tab_staff, name="tab_staff_paged"),
    url(r'^tabs/gallery/(?P<item>[0-9]+)/$', ChamberGalleryImageList.as_view(), name="tabs_gallery"),
    url(r'^tabs/gallery/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$', ChamberGalleryImageList.as_view(),
        name="tabs_gallery_paged"),
    url(r'^tabs/gallery_structure/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$',
        ChamberGalleryImageList.as_view(is_structure=True), name="gallery_structure"),
    url(r'^tabs/gallery/(?P<item>[0-9]+)/remove/(?P<pk>[0-9]+)/$',
        DeleteChamberGalleryImage.as_view(), name="gallery_remove_item"),

    url(r'^tabs/documents/(?P<item>[0-9]+)/$', ChamberDocumentList.as_view(), name="tabs_documents"),
    url(r'^tabs/documents/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$', ChamberDocumentList.as_view(),
        name="tabs_documents_paged"),
    url(r'^tabs/documents_structure/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$',
        ChamberDocumentList.as_view(is_structure=True), name="documents_structure"),
    url(r'^tabs/documents/(?P<item>[0-9]+)/remove/(?P<pk>[0-9]+)/$',
        DeleteChamberDocument.as_view(), name="documents_remove_item"),
]
