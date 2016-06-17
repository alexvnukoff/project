# -*- encoding: utf-8 -*-

"""
The 'Messages' application urls.
"""

from django.conf.urls import url

from usersites.Messages.views import (
    UsersitesChatsListView, 
    UsersitesChatMessagesView,
    add_to_chat,
)  

urlpatterns = [
    url(r'^$', UsersitesChatsListView.as_view(), name='main'),
    url(r'^chats/page(?P<page>[0-9]+)?/$', UsersitesChatsListView.as_view(), 
        name="chats_paginator"),
    url(r'^chats/add/$', add_to_chat, name='add_to_chat'),
    url(r'^chats/refresh/$', 
        UsersitesChatsListView.as_view(), 
        {'refresh': True},
        name='chats_list_refresh'),
    url(r'^chats/(?P<item_id>[0-9]+)/$', 
        UsersitesChatMessagesView.as_view(), 
        name='chat_messages'),
]
