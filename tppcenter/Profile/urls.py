from django.conf.urls import patterns, include, url
import appl.views
import tppcenter.Profile.views




from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.Profile.views.getProfileForm, name='main'),




)