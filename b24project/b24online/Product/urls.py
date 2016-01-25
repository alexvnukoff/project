from django.conf.urls import url

from b24online.Product.views import (B2BProductList, B2CProductList, 
    B2CPCouponsList, B2BProductCreate, B2BProductUpdate, 
    B2CProductCreate, B2CProductUpdate, B2BProductDelete, 
    B2CProductDelete, categories_list, B2BProductDetail, 
    B2CProductDetail, B2BProductGalleryImageList, 
    DeleteB2BProductGalleryImage, B2BProductDocumentList, 
    DeleteB2BProductDocument, B2BProductBuy, B2CProductBuy,
    DealOrderList, DealOrderDetail, DealOrderPayment,
    DealList, DealDetail, DealPayment, DealItemDelete)
    
from b24online.models import B2BProductCategory
from centerpokupok.models import B2CProductCategory

urlpatterns = [
    url(r'^b2b/$', B2BProductList.as_view(), name='main'),
    url(r'^page(?P<page>[0-9]+)?/$', B2BProductList.as_view(), name="paginator"),
    url(r'^my/$', B2BProductList.as_view(my=True), name='my_main'),
    url(r'^my/page(?P<page>[0-9]+)?/$', B2BProductList.as_view(my=True), name="my_main_paginator"),
    url(r'^b2c/$', B2CProductList.as_view(), name='main_b2c'),
    url(r'^my_b2c/$', B2CProductList.as_view(my=True), name='my_b2c'),
    url(r'^b2c/page(?P<page>[0-9]+)?/$', B2CProductList.as_view(), name="main_b2c_paginator"),
    url(r'^my_b2c/page(?P<page>[0-9]+)?/$', B2CProductList.as_view(my=True), name="my_b2c_paginator"),
    url(r'^сoupons/$', B2CPCouponsList.as_view(), name='main_сoupons'),
    url(r'^сoupons/page(?P<page>[0-9]+)?/$', B2CPCouponsList.as_view(), name="coupons_paginator"),
    url(r'^add/$', B2BProductCreate.as_view(), name="add"),
    url(r'^add-b2c/$', B2CProductCreate.as_view(), name="addB2C"),
    url(r'^update/(?P<pk>[0-9]+)/$', B2BProductUpdate.as_view(), name="update"),
    url(r'^update-b2c/(?P<pk>[0-9]+)/$', B2CProductUpdate.as_view(), name="updateB2C"),
    url(r'^delete/(?P<pk>[0-9]+)/$', B2BProductDelete.as_view(), name="delete"),
    url(r'^delete-b2c/(?P<pk>[0-9]+)/$', B2CProductDelete.as_view(), name="deleteB2C"),
    url(r'^category-list$', categories_list, {'model': B2BProductCategory}, name="B2BCategoryList"),
    url(r'^category-list-b2c$', categories_list, {'model': B2CProductCategory}, name="B2CCategoryList"),

    url(r'^b2b/buy/(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$', 
        B2BProductBuy.as_view(), name="buyB2B"),
    url(r'^b2c/buy/(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$', 
        B2CProductBuy.as_view(), name="buyB2C"),
    url(r'^b2b/(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$', B2BProductDetail.as_view(), name="detail"),
    url(r'^b2c/(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$', B2CProductDetail.as_view(), name="B2CDetail"),

    url(r'^tabs/gallery/(?P<item>[0-9]+)/$', B2BProductGalleryImageList.as_view(), name="tabs_gallery"),
    url(r'^tabs/gallery/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$',
        B2BProductGalleryImageList.as_view(), name="tabs_gallery_paged"),
    url(r'^tabs/gallery_structure/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$',
        B2BProductGalleryImageList.as_view(is_structure=True), name="gallery_structure"),
    url(r'^tabs/gallery/(?P<item>[0-9]+)/remove/(?P<pk>[0-9]+)/$',
        DeleteB2BProductGalleryImage.as_view(), name="gallery_remove_item"),
    url(r'^tabs/documents/(?P<item>[0-9]+)/$', B2BProductDocumentList.as_view(),
        name="tabs_documents"),
    url(r'^tabs/documents/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$',
        B2BProductDocumentList.as_view(), name="tabs_documents_paged"),
    url(r'^tabs/documents_structure/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$',
        B2BProductDocumentList.as_view(is_structure=True), name="documents_structure"),
    url(r'^tabs/documents/(?P<item>[0-9]+)/remove/(?P<pk>[0-9]+)/$',
        DeleteB2BProductDocument.as_view(), name="documents_remove_item"),

    # Urls for orders and deals 
    url(r'^orders/(?P<pk>[0-9]+)/$', 
        DealOrderDetail.as_view(), name="deal_order_detail"),
    url(r'^orders/(?P<pk>[0-9]+)/pay/$', 
        DealOrderPayment.as_view(), name="deal_order_payment"),
    url(r'^orders/$', 
        DealOrderList.as_view(), name="deal_order_list"),
    url(r'^orders/(?P<status>draft|ready|partially|paid)/$', 
        DealOrderList.as_view(), name="deal_order_filtered_list"),
    url(r'^deals/(?P<pk>[0-9]+)/$', 
        DealDetail.as_view(), name="deal_detail"),
    url(r'^deals/(?P<pk>[0-9]+)/$', 
        DealPayment.as_view(), name="deal_payment"),
    url(r'^deals/$', 
        DealList.as_view(), name="deal_list"),
    url(r'^deals/(?P<status>draft|ready|paid)/$', 
        DealList.as_view(), name="deal_filtered_list"),

    url(r'^deals/item/(?P<pk>[0-9]+)/delete/$', 
        DealItemDelete.as_view(), name="deal_item_delete"),

]
