__author__ = 'user'
from django.conf.urls import patterns, url

import b24online.Messages.views

urlpatterns = patterns('',
    # Examples:
     url(r'^$', b24online.Messages.views.view_messages, name='main'),
     url(r'^(?P<recipient_id>[0-9]+)/$', b24online.Messages.views.view_messages, name="message_item"),
     url(r'^add/$', b24online.Messages.views.add_message, name="add"),
)