from django.conf.urls import patterns, url
from django.contrib import admin

import b24online.Profile.views

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$', b24online.Profile.views.ProfileUpdate.as_view(), name='main'),
                       )
