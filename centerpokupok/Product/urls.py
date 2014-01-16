from django.conf.urls import patterns, include, url

import centerpokupok.Product.views

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', centerpokupok.Product.views.productList, name='list'),
     url(r'^([0-9]+)/$', centerpokupok.Product.views.productDetail, name="detail"),
     url(r'^comment/([0-9]+)/$', centerpokupok.Product.views.addComment, name="addComment"),

    # url(r'^blog/', include('blog.urls')),


)
