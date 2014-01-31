from django.conf.urls import patterns, include, url

import centerpokupok.company.views
import centerpokupok.Reviews.views

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^([0-9]+)/$', centerpokupok.company.views.storeMain, name="main"),
     url(r'^([0-9]+)/category/([0-9]+)/$', centerpokupok.Reviews.views.reviewDetail, name="category"),
     url(r'^([0-9]+)/products/$', centerpokupok.Reviews.views.reviewDetail, name="products"),
     url(r'^([0-9]+)/products/category/([0-9]+)/$', centerpokupok.Reviews.views.reviewDetail, name="product_category"),
     url(r'^([0-9]+)/coupons/$', centerpokupok.Reviews.views.reviewDetail, name="coupons"),
     url(r'^([0-9]+)/coupons/category/([0-9]+)/$', centerpokupok.Reviews.views.reviewDetail, name="coupons_category"),
     url(r'^([0-9]+)/about/$', centerpokupok.Reviews.views.reviewDetail, name="about"),
     url(r'^([0-9]+)/contact/$', centerpokupok.Reviews.views.reviewDetail, name="contact"),
    # url(r'^blog/', include('blog.urls')),


)
