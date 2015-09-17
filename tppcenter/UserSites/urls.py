from django.conf.urls import patterns, url
from django.contrib import admin

import tppcenter.UserSites.views
import tppcenter.views

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$', tppcenter.UserSites.views.form_dispatch, name='main'),
                       )
