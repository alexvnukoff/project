from django.conf.urls import patterns, include, url
import appl.views
import centerpokupok.views
import centerpokupok.News.urls
import centerpokupok.Product.urls

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', centerpokupok.views.home),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^about/$', centerpokupok.views.about),
    url(r'^news/', include("centerpokupok.News.urls")),
    url(r'^products/', include("centerpokupok.Product.urls")),


    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),


)
