from django.conf.urls import url

from b24online.BusinessProposal.views import BusinessProposalList, BusinessProposalCreate, BusinessProposalUpdate, \
    BusinessProposalDelete, BusinessProposalDetail, bp_categories_list, BPGalleryImageList, DeleteBPGalleryImage, \
    BPDocumentList, DeleteBPDocument

urlpatterns = [
    url(r'^$', BusinessProposalList.as_view(), name='main'),
    url(r'^page(?P<page>[0-9]+)?/$', BusinessProposalList.as_view(), name="paginator"),
    url(r'^my/$', BusinessProposalList.as_view(my=True), name='my_main'),
    url(r'^my/page(?P<page>[0-9]+)?/', BusinessProposalList.as_view(my=True), name="my_main_paginator"),
    url(r'^add/$', BusinessProposalCreate.as_view(), name="add"),
    url(r'^update/(?P<pk>[0-9]+)/$', BusinessProposalUpdate.as_view(), name="update"),
    url(r'^delete/(?P<pk>[0-9]+)/$', BusinessProposalDelete.as_view(), name="delete"),
    url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$', BusinessProposalDetail.as_view(), name="detail"),
    url(r'^bp-category-list$', bp_categories_list, name="BusinessProposalCategoryList"),

    url(r'^tabs/gallery/(?P<item>[0-9]+)/$', BPGalleryImageList.as_view(), name="tabs_gallery"),
    url(r'^tabs/gallery/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$',
        BPGalleryImageList.as_view(), name="tabs_gallery_paged"),
    url(r'^tabs/gallery_structure/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$',
        BPGalleryImageList.as_view(is_structure=True), name="gallery_structure"),
    url(r'^tabs/gallery/(?P<item>[0-9]+)/remove/(?P<pk>[0-9]+)/$',
        DeleteBPGalleryImage.as_view(), name="gallery_remove_item"),

    url(r'^tabs/documents/(?P<item>[0-9]+)/$', BPDocumentList.as_view(),
        name="tabs_documents"),
    url(r'^tabs/documents/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$',
        BPDocumentList.as_view(), name="tabs_documents_paged"),
    url(r'^tabs/documents_structure/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$',
        BPDocumentList.as_view(is_structure=True), name="documents_structure"),
    url(r'^tabs/documents/(?P<item>[0-9]+)/remove/(?P<pk>[0-9]+)/$',
        DeleteBPDocument.as_view(), name="documents_remove_item"),
]
