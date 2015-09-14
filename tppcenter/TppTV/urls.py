from django.conf.urls import patterns, url
from django.contrib import admin

import tppcenter.TppTV.views
import tppcenter.views

admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.TppTV.views.TVNewsLIst.as_view(), name='main'),
     url(r'^page(?P<page>[0-9]+)?/$', tppcenter.TppTV.views.TVNewsLIst.as_view(), name="paginator"),
     url(r'^add/$', tppcenter.TppTV.views.TvCreate.as_view(), name="add"),
     url(r'^update/(?P<pk>[0-9]+)/$', tppcenter.TppTV.views.TvUpdate.as_view(), name="update"),
     url(r'^delete/(?P<item_id>[0-9]+)/$', tppcenter.TppTV.views.tvForm, {'action': 'delete'}, name="delete"),
     url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$', tppcenter.TppTV.views.TVNewsDetail.as_view(), name="detail"),
)
