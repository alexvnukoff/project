# -*- encoding: utf-8 -*-

from django.conf.urls import url

from usersites.Messages.views import (
    UsersitesCharListView, 
    add_to_chat,

)  

urlpatterns = [
    url(r'^$', UsersitesCharListView.as_view(), name='main'),
    url(r'^chats/add/$', add_to_chat, name='add_to_chats'),
]
