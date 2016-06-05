# -*- encoding: utf-8 -*-

from django.conf.urls import url

from usersites.Messages.views import (
    view_chats, 
)  

urlpatterns = [
    url(r'^$', view_chats, name='main'),
]
