from django.conf.urls import patterns, include, url
import centerpokupok.Cabinet.views

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    url(r'^$', centerpokupok.Cabinet.views.get_profile, name="main"),
    url(r'^address/$', centerpokupok.Cabinet.views.get_shipping_detail, name="shipping_address"),
    url(r'^history/$', centerpokupok.Cabinet.views.get_order_history, name="order_history"),
    url(r'^history/page/([0-9]+)?/$', centerpokupok.Cabinet.views.get_order_history, name="paginator"),
    url(r'^favorite/$', centerpokupok.Cabinet.views.get_favorite, name="favorite"),
    url(r'^favorite/page/([0-9]+)?/$', centerpokupok.Cabinet.views.get_favorite, name="favorite_paginator"),


    # url(r'^blog/', include('blog.urls')),


)
