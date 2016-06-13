# -*- encoding: utf-8 -*-

"""
The 'Messages' application urls.
"""

from django.conf.urls import url

from usersites.Messages.views import (
    UsersitesChatsListView, 
    add_to_chat,
    ChatMessagesView,
)  

urlpatterns = [
    url(r'^$', UsersitesChatsListView.as_view(), name='main'),
    url(r'^chats/add/$', add_to_chat, name='add_to_chat'),
    url(r'^chats/(?P<item_id>[0-9]+)/$', ChatMessagesView.as_view(), 
        name='chat_messages'),
]
