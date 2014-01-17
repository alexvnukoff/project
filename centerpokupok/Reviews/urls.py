from django.conf.urls import patterns, include, url

import centerpokupok.Reviews.views

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', centerpokupok.Reviews.views.reviewList, name="list"),
     url(r'^([0-9]+)/$', centerpokupok.Reviews.views.reviewDetail, name="detail"),

    # url(r'^blog/', include('blog.urls')),


)
