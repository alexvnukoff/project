__author__ = 'user'
from django.conf.urls import patterns, include, url

import centerpokupok.Coupons.views

urlpatterns = patterns('',
    # Examples:
     url(r'^$', centerpokupok.Coupons.views.companyCoupontList.as_view(), name="list"),

     url(r'^page(?P<page>[0-9]+)/$',
         centerpokupok.Coupons.views.companyCoupontList.as_view(), name="list_paged"),

     url(r'^category([0-9]+)/$',
         centerpokupok.Coupons.views.companyCoupontList.as_view(), name="category"),

     url(r'^category([0-9]+)/page([0-9]+)/$',
         centerpokupok.Coupons.views.companyCoupontList.as_view(), name="category_paged"),

     url(r'^country/(?P<country>[0-9]+)/$',
         centerpokupok.Coupons.views.companyCoupontList.as_view(), name="list_country"),

     url(r'^country/(?P<country>[0-9]+)/page(?P<page>[0-9]+)/$',
         centerpokupok.Coupons.views.companyCoupontList.as_view(), name="list_country_paged"),

     url(r'^country/(?P<country>[0-9]+)/category(?P<currentCat>[0-9]+)/$',
         centerpokupok.Coupons.views.companyCoupontList.as_view(), name="category_country"),

     url(r'^country/(?P<country>[0-9]+)/category(?P<category>[0-9]+)/page(?P<page>[0-9]+)/$',
         centerpokupok.Coupons.views.companyCoupontList.as_view(), name="category_country_paged"),
)