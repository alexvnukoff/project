from django.conf.urls import patterns, url
from django.contrib import admin

import b24online.UserSites.views

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$', b24online.UserSites.views.form_dispatch, name='main'),
                       )
