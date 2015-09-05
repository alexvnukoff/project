from django.conf.urls import patterns, url
from django.contrib import admin

from b24online.models import B2BProductCategory
from centerpokupok.models import B2CProductCategory
import tppcenter.Product.views
import tppcenter.views

admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.Product.views.B2BProductList.as_view(), name='main'),
     url(r'^page(?P<page>[0-9]+)?/$', tppcenter.Product.views.B2BProductList.as_view(), name="paginator"),
     url(r'^my/$', tppcenter.Product.views.B2BProductList.as_view(my=True), name='my_main'),
     url(r'^my/page(?P<page>[0-9]+)?/$', tppcenter.Product.views.B2BProductList.as_view(my=True), name="my_main_paginator"),
     url(r'^b2c/$', tppcenter.Product.views.B2CProductList.as_view(my=True), name='my_main_b2c'),
     url(r'^b2c/page(?P<page>[0-9]+)?/$', tppcenter.Product.views.B2CProductList.as_view(my=True), name="my_main_b2c_paginator"),
     url(r'^add/$', tppcenter.Product.views.B2BProductCreate.as_view(), name="add"),
     url(r'^add-b2c/$', tppcenter.Product.views.B2CProductCreate.as_view(), name="addB2C"),
     url(r'^update/(?P<pk>[0-9]+)/$', tppcenter.Product.views.B2BProductUpdate.as_view(), name="update"),
     url(r'^update-b2c/(?P<pk>[0-9]+)/$', tppcenter.Product.views.B2CProductUpdate.as_view(), name="updateB2C"),
     url(r'^delete/(?P<item_id>[0-9]+)/$', tppcenter.Product.views.productForm, {'action': 'delete'}, name="delete"),
     url(r'^category-list$', tppcenter.Product.views.categories_list, {'model': B2BProductCategory}, name="B2BCategoryList"),
     url(r'^category-list-b2c$', tppcenter.Product.views.categories_list, {'model': B2CProductCategory}, name="B2CCategoryList"),
     url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$', tppcenter.Product.views.B2BProductDetail.as_view(), name="detail"),
     url(r'^b2c/(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$', tppcenter.Product.views.B2CProductDetail.as_view(), name="B2CDetail"),
)
