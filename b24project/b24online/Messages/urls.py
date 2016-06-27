# -*- encoding: utf-8 -*-

from django.conf.urls import url

from b24online.Messages.views import (
    view_messages, 
    add_message,
    chat_messages,
    add_to_chat,
    send_message,
    add_participant,
    update_chat,
    leave_chat,
    ChatListView,
)  

urlpatterns = [
    url(r'^$', ChatListView.as_view(), name='main'),
    url(r'^(?P<recipient_id>[0-9]+)/$', view_messages, name='message_item'),
    url(r'^add/$', add_message, name='add'),
    url(r'^chats/$', ChatListView.as_view(), name='chats'),
    url(r'^chats/page(?P<page>[0-9]+)?/$', ChatListView.as_view(), 
        name="chats_paginator"),
    url(r'^chats/add/$', add_to_chat, name='add_to_chats'),
    url(r'^chats/(?P<item_id>[0-9]+)/$', chat_messages, 
        name='chat_messages'),
    url(r'^chats/(?P<item_id>[0-9]+)/participant/add/$', add_participant, 
        name='add_participant'),
    url(r'^chats/(?P<item_id>[0-9]+)/update/$', update_chat, 
        name='update_chat'),
    url(r'^chats/(?P<item_id>[0-9]+)/leave/$', leave_chat, 
        name='leave_chat'),
    url(r'^send/(?P<recipient_type>organization|user)/(?P<item_id>[0-9]+)/$', 
        send_message, name='send_message_to_recipient'),
    url(r'^send/$', send_message, name='send_message'),
]
