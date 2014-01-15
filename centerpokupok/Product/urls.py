from django.conf.urls import patterns, include, url

import centerpokupok.Product.views

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', centerpokupok.Product.views.productList),
     url(r'^([0-9]+)/$', centerpokupok.Product.views.productDetail),

    # url(r'^blog/', include('blog.urls')),


)
