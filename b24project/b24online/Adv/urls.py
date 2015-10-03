from django.conf.urls import url, patterns

__author__ = 'Art'

import b24online.Adv.views

urlpatterns = patterns('',
    # Examples:
     url(r'^$', b24online.Adv.views.basket, name='main'),
     url(r'^page/(?P<page>[0-9]+)?/$', b24online.Adv.views.basket, name="paginator"),
)