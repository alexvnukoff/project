from django.conf.urls import patterns, include, url
import appl.views
import tppcenter.Product.views

import tppcenter.views


from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.Product.views.B2BProductList.as_view(), name='main'),
     url(r'^page(?P<page>[0-9]+)?/$', tppcenter.Product.views.B2BProductList.as_view(), name="paginator"),
     url(r'^my/$', tppcenter.Product.views.B2BProductList.as_view(my=True), name='my_main'),
     url(r'^my/page(?P<page>[0-9]+)?/$', tppcenter.Product.views.B2BProductList.as_view(my=True), name="my_main_paginator"),
     url(r'^b2c/$', tppcenter.Product.views.B2CProductList.as_view(my=True), name='my_main_b2c'),
     url(r'^b2c/page(?P<page>[0-9]+)?/$', tppcenter.Product.views.B2CProductList.as_view(my=True), name="my_main_b2c_paginator"),
     url(r'^add/$', tppcenter.Product.views.B2BProductCreate.as_view()     ,{'action': 'add'}, name="add"),
     url(r'^add-b2c/$', tppcenter.Product.views.productForm,{'action': 'add_b2c'}, name="addB2C"),
     url(r'^update/(?P<item_id>[0-9]+)/$', tppcenter.Product.views.productForm, {'action': 'update'}, name="update"),
     url(r'^update-b2c/(?P<item_id>[0-9]+)/$', tppcenter.Product.views.productForm, {'action': 'update_b2c'}, name="updateB2C"),
     url(r'^delete/(?P<item_id>[0-9]+)/$', tppcenter.Product.views.productForm, {'action': 'delete'}, name="delete"),
     url(r'^category-list/([0-9]+)/$', tppcenter.Product.views.categoryList, name="categoryList"),
     url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$', tppcenter.Product.views.ProductDetail.as_view(), name="detail"),
)