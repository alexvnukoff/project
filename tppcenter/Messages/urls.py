__author__ = 'user'
from django.conf.urls import patterns, include, url
import appl.views
import tppcenter.Messages.views

urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.Messages.views.view_messages, name='main'),
     url(r'^(?P<recipient_id>[0-9]+)/$', tppcenter.Messages.views.view_messages, name="message_item"),
     url(r'^add/$', tppcenter.Messages.views.add_message, name="add"),
)