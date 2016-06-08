# -*- encoding: utf-8 -*-

import logging

from b24online.Messages.views import ChatListView
from usersites.mixins import UserTemplateMixin
from usersites.Messages.forms import MessageForm


class UsersitesCharListView(UserTemplateMixin, ChatListView):
    template_name = '{template_path}/Messages/chats.html'

    def get_context_data(self, **kwargs):
        context = super(UsersitesCharListView, self)\
            .get_context_data(**kwargs)
            
        new_message_form = MessageForm(
            self.request,
            data=self.request.POST,
            files=self.request.FILES) \
        if self.request.method == 'POST' else MessageForm(self.request)

        context.update({'new_message_form': new_message_form})
        return context
