__author__ = 'user'
from django.conf.urls import patterns, include, url
import appl.views
import tppcenter.Messages.views

urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.Messages.views.viewMessages, name='main'),
     url(r'^(?P<item_id>[0-9]+)/$', tppcenter.Messages.views.viewMessages, name="message_item"),
     url(r'^add/$', tppcenter.Messages.views.addMessages),
)