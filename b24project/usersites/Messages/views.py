# -*- encoding: utf-8 -*-

import json
import logging

from django.contrib.auth.decorators import login_required
from django.http import (HttpResponse, HttpResponseBadRequest, Http404, 
                         HttpResponseRedirect)
from django.utils.translation import ugettext as _
from django.utils.html import strip_tags
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


@login_required
def add_to_chat(request):
    response_code = 'error'
    response_text = 'Error'
    data = {}
    if request.method == 'POST':
        form = MessageForm(request, data=request.POST, files=request.FILES)
        if form.is_valid():
            try:
                form.send()
            except IntegrityError as exc:
                data.update({
                    'code': 'error',
                    'msg': _('Error during data saving') + str(exc),
                })
            else:
                data.update({
                    'code': 'success',
                    'msg': _('You have successfully updated chat'),
                })
        else:
            data.update({
                'code': 'error',
                'errors': form.get_errors(),
                'msg': _('There are some errors'),
            })
        return HttpResponse(
            json.dumps(data),
            content_type='application/json'
        )
    return HttpResponseBadRequest()
