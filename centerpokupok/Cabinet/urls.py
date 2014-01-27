from django.conf.urls import patterns, include, url
import centerpokupok.Cabinet.views

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    url(r'^$', centerpokupok.Cabinet.views.get_profile, name="main"),


    # url(r'^blog/', include('blog.urls')),


)
