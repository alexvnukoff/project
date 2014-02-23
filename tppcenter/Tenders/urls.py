from django.conf.urls import patterns, include, url
import appl.views
import tppcenter.Tenders.views

import tppcenter.views


from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.Tenders.views.get_tenders_list, name='main'),
     url(r'^page/?P<page>([0-9]+)?/$', tppcenter.Tenders.views.get_tenders_list, name="paginator"),
     url(r'^add/$', tppcenter.Tenders.views.addTender, name="add"),
     url(r'^update/([0-9]+)/$', tppcenter.Tenders.views.updateTender, name="update"),
     url(r'^[a-zA-z0-9-]+-(?P<item_id>[0-9]+).html$', tppcenter.Tenders.views.get_tenders_list, name="detail"),






)