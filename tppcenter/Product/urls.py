from django.conf.urls import patterns, include, url
import appl.views
import tppcenter.Product.views

import tppcenter.views


from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.Product.views.get_product_list, name='main'),
     url(r'^page/([0-9]+)?/$', tppcenter.Product.views.get_product_list, name="paginator"),






)