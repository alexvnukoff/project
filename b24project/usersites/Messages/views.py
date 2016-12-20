# -*- encoding: utf-8 -*-

import logging

from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.http import (HttpResponseBadRequest, JsonResponse)
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.views.generic.base import TemplateView
from guardian.mixins import LoginRequiredMixin

from b24online.cbv import (ItemDetail, ItemsList)
from b24online.models import (MessageChat, MessageChatParticipant)
from tpp.DynamicSiteMiddleware import get_current_site
from usersites.Messages.forms import MessageForm
from usersites.mixins import UserTemplateMixin

logger = logging.getLogger(__name__)


class UsersitesChatsListView(UserTemplateMixin, ItemsList):
    """The user's chats list"""
    template_name = '{template_path}/Messages/chats.html'
    paginate_by = 10
    model = MessageChat
    url_paginator = "messages:chats_paginator"
    scripts = []
    styles = []
    without_json = True

    def get_context_data(self, **kwargs):
        context = super(UsersitesChatsListView, self).get_context_data(**kwargs)
        self.object_list = self.get_queryset()

        only_refresh = self.kwargs.get('refresh')

        if not only_refresh:
            new_message_form = MessageForm(
                self.request,
                data=self.request.POST,
                files=self.request.FILES) \
            if self.request.method == 'POST' else MessageForm(self.request)
            context.update({
                'new_message_form': new_message_form,
                'participant': self.participant,
            })
        else:
            self.template_name = '{template_path}/Messages/chatsRefresh.html'

        return context

    def get_queryset(self):
        self.participant = MessageChatParticipant.get_instance(
            request=self.request
        )
        self.organization = get_current_site().user_site.organization
        if self.participant:
            chats = self.model.objects\
                .filter(organization=self.organization,
                        participants__id__exact=self.participant.id,
                        status=MessageChat.OPENED)\
                .distinct()\
                .order_by('-updated_at')
        else:
            chats = self.model.objects.none()
        return chats


def add_to_chat(request):
    response_code, response_text = 'error', 'Error'
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
        return JsonResponse(data)

    return HttpResponseBadRequest()


class UsersitesChatMessagesView(UserTemplateMixin, 
                                ItemDetail):
    """The chat's messages view"""
    model = MessageChat
    template_name = '{template_path}/Messages/chatMessages.html'
    messages_per_page = 5

    def get_context_data(self, **kwargs):
        context = super(UsersitesChatMessagesView, self)\
            .get_context_data(**kwargs)
        participant = MessageChatParticipant.get_instance(
            request=self.request
        )
        if participant.id in [p.id for p in self.object.participants.all()]:
            messages = self.object.chat_messages.all()
            messages_cnt = messages.count()
            if messages_cnt > self.messages_per_page:
                messages = messages.order_by('created_at')\
                    [messages_cnt - self.messages_per_page:]
            else:
                messages = messages.order_by('created_at')
        else:
            messages = Message.objects.none()
        context = {
            'chat': self.object,
            'messages': messages,
        }
        return context


class OnlineAdviserView(TemplateView):

    template_name = 'usersites/Messages/onlineAdviser.html'

    def get_context_data(self, **kwargs):
        context = super(OnlineAdviserView, self).get_context_data(**kwargs)
        context['new_message_form'] = MessageForm(self.request, compact=True)
        return context

