__author__ = 'user'
from django.conf.urls import patterns, include, url

import centerpokupok.Coupons.views

urlpatterns = patterns('',
    # Examples:
     url(r'^$', centerpokupok.Coupons.views.couponsList, name="list"),
     url(r'^category/([0-9]+)/$', centerpokupok.Coupons.views.couponsList, name="category"),
)