from django.conf.urls import url

from b24online.Companies.views import CompanyList, CompanyCreate, CompanyUpdate, DeleteCompany, CompanyDetail, \
    send_message, _tab_news, _tab_tenders, _tabs_exhibitions, _tab_products, _tab_structure, _tab_staff, _tab_proposals, \
    _tab_innovation_projects, CompanyGalleryImageList, DeleteCompanyGalleryImage, CompanyDocumentList, \
    DeleteCompanyDocument

urlpatterns = [
    url(r'^$', CompanyList.as_view(), name='main'),

    url(r'^page(?P<page>[0-9]+)?/$', CompanyList.as_view(), name="paginator"),
    url(r'^my/$', CompanyList.as_view(my=True), name='my_main'),
    url(r'^my/page(?P<page>[0-9]+)?/$', CompanyList.as_view(my=True), name="my_main_paginator"),
    url(r'^add/$', CompanyCreate.as_view(), name="add"),
    url(r'^update/(?P<pk>[0-9]+)/$', CompanyUpdate.as_view(), name="update"),
    url(r'^delete/(?P<pk>[0-9]+)/$', DeleteCompany.as_view(), {'action': "delete"}, name="delete"),
    url(r'^(?P<slug>[0-9a-zA-z-]+)-(?P<item_id>[0-9]+)\.html$', CompanyDetail.as_view(), name="detail"),
    url(r'^send/$', send_message),

    url(r'^tabs/news/(?P<company>[0-9]+)/$', _tab_news, name="tab_news"),
    url(r'^tabs/news/(?P<company>[0-9]+)/page(?P<page>[0-9]+)/$', _tab_news, name="tab_news_paged"),
    url(r'^tabs/tenders/(?P<company>[0-9]+)/$', _tab_tenders, name="tab_tenders"),
    url(r'^tabs/tenders/(?P<company>[0-9]+)/page(?P<page>[0-9]+)/$', _tab_tenders, name="tab_tenders_paged"),
    url(r'^tabs/exhibitions/(?P<company>[0-9]+)/$', _tabs_exhibitions, name="tab_exhibitions"),
    url(r'^tabs/exhibitions/(?P<company>[0-9]+)/page(?P<page>[0-9]+)/$', _tabs_exhibitions,
        name="tab_exhibitions_paged"),
    url(r'^tabs/products/(?P<company>[0-9]+)/$', _tab_products, name="tab_products"),
    url(r'^tabs/products/(?P<company>[0-9]+)/page(?P<page>[0-9]+)/$', _tab_products, name="tab_products_paged"),
    url(r'^tabs/structure/(?P<company>[0-9]+)/$', _tab_structure, name="tab_structure"),
    url(r'^tabs/structure/(?P<company>[0-9]+)/page(?P<page>[0-9]+)/$', _tab_structure, name="tab_structure_paged"),
    url(r'^tabs/staff/(?P<company>[0-9]+)/$', _tab_staff, name="tab_staff"),
    url(r'^tabs/staff/(?P<company>[0-9]+)/page(?P<page>[0-9]+)/$', _tab_staff, name="tab_staff_paged"),
    url(r'^tabs/proposal/(?P<company>[0-9]+)/$', _tab_proposals, name="tab_proposal"),
    url(r'^tabs/proposal/(?P<company>[0-9]+)/page(?P<page>[0-9]+)/$', _tab_proposals, name="tab_proposal_paged"),
    url(r'^tabs/innov/(?P<company>[0-9]+)/$', _tab_innovation_projects, name="tab_innov"),
    url(r'^tabs/innov/(?P<company>[0-9]+)/page(?P<page>[0-9]+)/$', _tab_innovation_projects, name="tab_innov_paged"),
    url(r'^tabs/gallery/(?P<item>[0-9]+)/$', CompanyGalleryImageList.as_view(), name="tabs_gallery"),
    url(r'^tabs/gallery/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$',
        CompanyGalleryImageList.as_view(), name="tabs_gallery_paged"),
    url(r'^tabs/gallery_structure/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$',
        CompanyGalleryImageList.as_view(is_structure=True), name="gallery_structure"),
    url(r'^tabs/gallery/(?P<item>[0-9]+)/remove/(?P<pk>[0-9]+)/$',
        DeleteCompanyGalleryImage.as_view(), name="gallery_remove_item"),

    url(r'^tabs/documents/(?P<item>[0-9]+)/$', CompanyDocumentList.as_view(), name="tabs_documents"),
    url(r'^tabs/documents/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$',
        CompanyDocumentList.as_view(), name="tabs_documents_paged"),
    url(r'^tabs/documents_structure/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$',
        CompanyDocumentList.as_view(is_structure=True), name="documents_structure"),
    url(r'^tabs/documents/(?P<item>[0-9]+)/remove/(?P<pk>[0-9]+)/$',
        DeleteCompanyDocument.as_view(), name="documents_remove_item"),
]
