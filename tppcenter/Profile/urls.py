from django.conf.urls import patterns, url
from django.contrib import admin

import tppcenter.Profile.views

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$', tppcenter.Profile.views.ProfileUpdate.as_view(), name='main'),
                       )
