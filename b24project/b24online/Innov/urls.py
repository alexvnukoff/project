from django.conf.urls import url

from b24online.Innov.views import InnovationProjectList, InnovationProjectCreate, InnovationProjectUpdate, \
    InnovationProjectDetail, InnovGalleryImageList, InnovationProjectDelete, InnovDocumentList, DeleteInnovDocument, \
    DeleteInnovGalleryImage

urlpatterns = [
    url(r'^$', InnovationProjectList.as_view(), name='main'),

    url(r'^page(?P<page>[0-9]+)?/$', InnovationProjectList.as_view(), name="paginator"),
    url(r'^my/$', InnovationProjectList.as_view(my=True), name='my_main'),
    url(r'^my/page(?P<page>[0-9]+)?/$', InnovationProjectList.as_view(my=True), name="my_main_paginator"),
    url(r'^add/$', InnovationProjectCreate.as_view(), name="add"),
    url(r'^update/(?P<pk>[0-9]+)/$', InnovationProjectUpdate.as_view(), name="update"),
    url(r'^delete/(?P<pk>[0-9]+)/$', InnovationProjectDelete.as_view(), name="delete"),
    url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$', InnovationProjectDetail.as_view(), name="detail"),

    url(r'^tabs/gallery/(?P<item>[0-9]+)/$', InnovGalleryImageList.as_view(), name="tabs_gallery"),
    url(r'^tabs/gallery/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$', InnovGalleryImageList.as_view(),
        name="tabs_gallery_paged"),
    url(r'^tabs/gallery_structure/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$',
        InnovGalleryImageList.as_view(is_structure=True), name="gallery_structure"),
    url(r'^tabs/gallery/(?P<item>[0-9]+)/remove/(?P<pk>[0-9]+)/$',
        DeleteInnovGalleryImage.as_view(), name="gallery_remove_item"),

    url(r'^tabs/documents/(?P<item>[0-9]+)/$', InnovDocumentList.as_view(), name="tabs_documents"),
    url(r'^tabs/documents/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$', InnovDocumentList.as_view(),
        name="tabs_documents_paged"),
    url(r'^tabs/documents_structure/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$',
        InnovDocumentList.as_view(is_structure=True), name="documents_structure"),
    url(r'^tabs/documents/(?P<item>[0-9]+)/remove/(?P<pk>[0-9]+)/$',
        DeleteInnovDocument.as_view(), name="documents_remove_item"),
]
