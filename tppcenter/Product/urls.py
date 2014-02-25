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
     url(r'^add/$', tppcenter.Product.views.addProducts, name="add"),
     url(r'^update/([0-9]+)/$', tppcenter.Product.views.updateProduct, name="update"),
     url(r'^[a-zA-z0-9-]+-(?P<item_id>[0-9]+).html$', tppcenter.Product.views.get_product_list, name="detail"),






)