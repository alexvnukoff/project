from django.conf.urls import patterns, include, url
import appl.views
import tppcenter.Product.views

import tppcenter.views


from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.Product.views.get_product_list, name='main'),
     url(r'^page(?P<page>[0-9]+)?/$', tppcenter.Product.views.get_product_list, name="paginator"),
     url(r'^my/$', tppcenter.Product.views.get_product_list,{'my':True}, name='my_main'),
     url(r'^my/page(?P<page>[0-9]+)?/$', tppcenter.Product.views.get_product_list,{'my':True}, name="my_main_paginator"),
     url(r'^add/$', tppcenter.Product.views.productForm,{'action': 'add'}, name="add"),
     url(r'^update/(?P<item_id>[0-9]+)/$', tppcenter.Product.views.productForm,{'action': 'update'}, name="update"),
     url(r'^(?P<slug>[a-zA-z0-9-]+-(?P<item_id>[0-9]+))\.html$', tppcenter.Product.views.get_product_list, name="detail"),






)