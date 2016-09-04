# -*- encoding: utf-8 -*-

import json
import logging

from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.http import (HttpResponse, HttpResponseBadRequest)
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from guardian.mixins import LoginRequiredMixin

from b24online.cbv import (ItemDetail, ItemsList)
from b24online.models import (MessageChat)
from tpp.DynamicSiteMiddleware import get_current_site
from usersites.Messages.forms import MessageForm
from usersites.mixins import UserTemplateMixin

logger = logging.getLogger(__name__)


class UsersitesChatsListView(LoginRequiredMixin, UserTemplateMixin, 
                             ItemsList):
    """The user's chats list"""
    template_name = '{template_path}/Messages/chats.html'
    paginate_by = 10
    model = MessageChat
    url_paginator = "messages:chats_paginator"
    scripts = []
    styles = []
    without_json = True
    
    def get_context_data(self, **kwargs):
        context = super(UsersitesChatsListView, self)\
            .get_context_data(**kwargs)
        self.object_list = self.get_queryset()
        only_refresh = self.kwargs.get('refresh')
        if not only_refresh:
            new_message_form = MessageForm(
                self.request,
                data=self.request.POST,
                files=self.request.FILES) \
            if self.request.method == 'POST' else MessageForm(self.request)
            context.update({'new_message_form': new_message_form})
        else:
            self.template_name = '{template_path}/Messages/chatsRefresh.html'
        return context

    def get_queryset(self):
        self.organization = get_current_site().user_site.organization
        chats = self.model.objects\
            .filter(organization=self.organization,
                    participants__id__exact=self.request.user.id,
                    status=MessageChat.OPENED)\
            .distinct()\
            .order_by('-updated_at')
        return chats


@login_required
def add_to_chat(request):
    response_code = 'error'
    response_text = 'Error'
    data = {}
    if request.method == 'POST':
        form = MessageForm(request, data=request.POST,
                           files=request.FILES)
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


class UsersitesChatMessagesView(LoginRequiredMixin, UserTemplateMixin, 
                                ItemDetail):
    """The chat's messages view"""
    model = MessageChat
    template_name = '{template_path}/Messages/chatMessages.html'
    messages_per_page = 5

    def get_context_data(self, **kwargs):
        context = super(UsersitesChatMessagesView, self)\
            .get_context_data(**kwargs)
        messages = self.object.chat_messages.all()
        messages_cnt = messages.count()
        if messages_cnt > self.messages_per_page:
            messages = messages.order_by('created_at')\
                [messages_cnt - self.messages_per_page:]
        else:
            messages = messages.order_by('created_at')
        context = {
            'chat': self.object,
            'messages': messages,
        }
        return context


def online_adviser(request, *args, **kwargs):
    template_name = 'usersites/Messages/onlineAdviser.html'
    form = MessageForm(request, compact=True)
    context = {'new_message_form': form}
    data = {
        'title': _(u'Your question'),
        'msg': render_to_string(template_name, context, 
            context_instance=RequestContext(request))
    }
    return HttpResponse(
        json.dumps(data),
        content_type='application/json'
    )
