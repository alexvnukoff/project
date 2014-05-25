from django.conf.urls import url, patterns

__author__ = 'Art'

import tppcenter.Adv.views

urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.Adv.views.basket, name='main'),
     url(r'^page/(?P<page>[0-9]+)?/$', tppcenter.Adv.views.basket, name="paginator"),
)