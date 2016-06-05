# -*- encoding: utf-8 -*-

from django.conf.urls import url

from usersites.Messages.views import (
    UsersitesCharListView, 
)  

urlpatterns = [
    url(r'^$', UsersitesCharListView.as_view(), name='main'),
]
