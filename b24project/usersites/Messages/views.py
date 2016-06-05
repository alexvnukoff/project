# -*- encoding: utf-8 -*-

import logging

from b24online.Messages.views import ChatListView
from usersites.mixins import UserTemplateMixin


class UsersitesCharListView(UserTemplateMixin, ChatListView):
    template_name = '{template_path}/Messages/chats.html'
