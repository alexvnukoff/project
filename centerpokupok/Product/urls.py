from django.conf.urls import patterns, include, url

import centerpokupok.Product.views

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', centerpokupok.Product.views.getAllNewProducts, name='list'),
     url(r'^page/([0-9]+)/$', centerpokupok.Product.views.getAllNewProducts, name='products_paginator'),
     url(r'^([0-9]+)/$', centerpokupok.Product.views.productDetail, name="detail"),
     url(r'^([0-9]+)/page/([0-9]+)/$', centerpokupok.Product.views.productDetail, name="paginator"),
     url(r'^comment/([0-9]+)/$', centerpokupok.Product.views.addComment, name="addComment"),
     url(r'^category/([0-9]+)/$', centerpokupok.Product.views.getCategoryProduct, name="category"),
     url(r'^category/([0-9]+)/page/([0-9]+)/$', centerpokupok.Product.views.getCategoryProduct, name="cat_pagination"),

    # url(r'^blog/', include('blog.urls')),


)
