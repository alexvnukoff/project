from django.conf.urls import patterns, include, url

import centerpokupok.Product.views

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', centerpokupok.Product.views.getProductList.as_view(), name='list'),
     url(r'^country/(?P<country>[0-9]+)/$', centerpokupok.Product.views.getProductList.as_view(), name='country_products'),
     url(r'^country/(?P<country>[0-9]+)/page/(?P<page>[0-9]+)/$', centerpokupok.Product.views.getProductList.as_view(), name='country_products_paginator'),
     url(r'^page/(?P<page>[0-9]+)/$', centerpokupok.Product.views.getProductList.as_view(), name='products_paginator'),
     url(r'^([0-9]+)/$', centerpokupok.Product.views.productDetail, name="detail"),
     url(r'^([0-9]+)/page/([0-9]+)/$', centerpokupok.Product.views.productDetail, name="paginator"),
     url(r'^comment/([0-9]+)/$', centerpokupok.Product.views.addComment, name="addComment"),
     url(r'^category/(?P<category>[0-9]+)/$', centerpokupok.Product.views.getProductList.as_view(), name="category"),
     url(r'^country/(?P<country>[0-9]+)/category/(?P<category>[0-9]+)/$', centerpokupok.Product.views.getProductList.as_view(), name="category_country"),
     url(r'^country/(?P<country>[0-9]+)/category/(?P<category>[0-9]+)/page/(?P<page>[0-9]+)/$', centerpokupok.Product.views.getProductList.as_view(), name="category_country_paginator"),
     url(r'^category/(?P<category>[0-9]+)/page/(?P<page>[0-9]+)/$', centerpokupok.Product.views.getProductList.as_view(), name="cat_pagination"),
     url(r'^order/step/(1|2|3)/$', centerpokupok.Product.views.orderProduct, name="order"),
     url(r'^addToFavorite/$', centerpokupok.Product.views.addFavorite, name="favorite"),
    # url(r'^blog/', include('blog.urls')),
)
