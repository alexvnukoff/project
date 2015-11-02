from django.conf.urls import patterns, include, url

import centerpokupok.Categories.views

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', centerpokupok.Categories.views.categoryList, name="list"),





)
