# -*- encoding: utf-8 -*-

from django.conf.urls import url

from b24online.Messages.views import (
    view_messages, 
    add_message,
    view_chats, 
    chat_messages,
    add_to_chat,
    send_message,
)  

urlpatterns = [
    url(r'^$', view_chats, name='main'),
    url(r'^(?P<recipient_id>[0-9]+)/$', view_messages, name="message_item"),
    url(r'^add/$', add_message, name="add"),
    url(r'^chats/$', view_chats, name='chats'),
    url(r'^chats/add/$', add_to_chat, name='add_to_chats'),
    url(r'^chats/(?P<item_id>[0-9]+)/$', chat_messages, 
        name="chat_messages"),
    url(r'^send/(?P<recipient_type>organization|user)/(?P<item_id>[0-9]+)/$', 
        send_message, name='send_message'),
]
