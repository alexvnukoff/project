from django.conf.urls import patterns, include, url
import appl.views
import tppcenter.Tenders.views

import tppcenter.views


from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.Tenders.views.get_tenders_list, name='main'),
     url(r'^page/([0-9]+)?/$', tppcenter.Tenders.views.get_tenders_list, name="paginator"),






)