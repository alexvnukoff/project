from django.conf.urls import url

import b24online.Product.views
from b24online.models import B2BProductCategory
from centerpokupok.models import B2CProductCategory

urlpatterns = [
    url(r'^b2b/$', b24online.Product.views.B2BProductList.as_view(), name='main'),
    url(r'^page(?P<page>[0-9]+)?/$', b24online.Product.views.B2BProductList.as_view(), name="paginator"),
    url(r'^my/$', b24online.Product.views.B2BProductList.as_view(my=True), name='my_main'),
    url(r'^my/page(?P<page>[0-9]+)?/$', b24online.Product.views.B2BProductList.as_view(my=True),
        name="my_main_paginator"),
    url(r'^b2c/$', b24online.Product.views.B2CProductList.as_view(), name='main_b2c'),
    url(r'^my_b2c/$', b24online.Product.views.B2CProductList.as_view(my=True), name='my_b2c'),
    url(r'^b2c/page(?P<page>[0-9]+)?/$', b24online.Product.views.B2CProductList.as_view(), name="main_b2c_paginator"),
    url(r'^my_b2c/page(?P<page>[0-9]+)?/$', b24online.Product.views.B2CProductList.as_view(my=True),
        name="my_b2c_paginator"),
    url(r'^сoupons/$', b24online.Product.views.B2CPCouponsList.as_view(), name='main_сoupons'),
    url(r'^сoupons/page(?P<page>[0-9]+)?/$', b24online.Product.views.B2CPCouponsList.as_view(),
        name="coupons_paginator"),
    url(r'^add/$', b24online.Product.views.B2BProductCreate.as_view(), name="add"),
    url(r'^add-b2c/$', b24online.Product.views.B2CProductCreate.as_view(), name="addB2C"),
    url(r'^update/(?P<pk>[0-9]+)/$', b24online.Product.views.B2BProductUpdate.as_view(), name="update"),
    url(r'^update-b2c/(?P<pk>[0-9]+)/$', b24online.Product.views.B2CProductUpdate.as_view(), name="updateB2C"),
    url(r'^delete/(?P<pk>[0-9]+)/$', b24online.Product.views.B2BProductDelete.as_view(), name="delete"),
    url(r'^delete-b2c/(?P<pk>[0-9]+)/$', b24online.Product.views.B2CProductDelete.as_view(), name="deleteB2C"),
    url(r'^category-list$', b24online.Product.views.categories_list, {'model': B2BProductCategory},
        name="B2BCategoryList"),
    url(r'^category-list-b2c$', b24online.Product.views.categories_list, {'model': B2CProductCategory},
        name="B2CCategoryList"),
    url(r'^b2b/(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$', b24online.Product.views.B2BProductDetail.as_view(),
        name="detail"),
    url(r'^b2c/(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$', b24online.Product.views.B2CProductDetail.as_view(),
        name="B2CDetail"),

    url(r'^tabs/gallery/(?P<item>[0-9]+)/$', b24online.Product.views.B2BProductGalleryImageList.as_view(),
        name="tabs_gallery"),
    url(r'^tabs/gallery/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$',
        b24online.Product.views.B2BProductGalleryImageList.as_view(), name="tabs_gallery_paged"),
    url(r'^tabs/gallery_structure/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$',
        b24online.Product.views.B2BProductGalleryImageList.as_view(is_structure=True), name="gallery_structure"),
    url(r'^tabs/gallery/(?P<item>[0-9]+)/remove/(?P<pk>[0-9]+)/$',
        b24online.Product.views.DeleteB2BProductGalleryImage.as_view(), name="gallery_remove_item"),

    url(r'^tabs/documents/(?P<item>[0-9]+)/$', b24online.Product.views.B2BProductDocumentList.as_view(),
        name="tabs_documents"),
    url(r'^tabs/documents/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$',
        b24online.Product.views.B2BProductDocumentList.as_view(), name="tabs_documents_paged"),
    url(r'^tabs/documents_structure/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$',
        b24online.Product.views.B2BProductDocumentList.as_view(is_structure=True), name="documents_structure"),
    url(r'^tabs/documents/(?P<item>[0-9]+)/remove/(?P<pk>[0-9]+)/$',
        b24online.Product.views.DeleteB2BProductDocument.as_view(), name="documents_remove_item"),
]
