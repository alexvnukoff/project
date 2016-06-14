# -*- encoding: utf-8 -*-

"""
Forms for `Message` application.
"""

import logging

from django.db import transaction, IntegrityError

from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _
from django.utils.html import strip_tags

from b24online.models import (User, Organization, MessageChat,
                              Message, MessageAttachment, Vacancy)
from b24online.utils import handle_uploaded_file
from b24online import InvalidParametersError
from tpp.DynamicSiteMiddleware import get_current_site

logger = logging.getLogger(__name__)


class MessageForm(forms.ModelForm):
    """
    The new message and chat form class.
    """
    chat = forms.ModelChoiceField(
        queryset=MessageChat.objects.all(),
        required=False
    )
    recipient = forms.ChoiceField(
        choices=(),
        label=_('Message recipient'),
        required=False,
    )
    attachment = forms.FileField(
        label=_('Message attachment'),
        required=False
    )

    class Meta:
        model = Message
        fields = ('subject', 'content')

    def __init__(self, request, *args, **kwargs):
        self.request = request
        self.organization = get_current_site().user_site.organization
        self.chat = kwargs.pop('chat', None)
        super(MessageForm, self).__init__(*args, **kwargs)
        self.fields['recipient'].choices = self.get_organization_staff()
        self.fields['content'].required = True
        if self.chat:
            self.fields['recipient'] = False
        for field_name in ('subject', 'content', 'recipient'):
            self.fields[field_name].widget.attrs\
                .update({'class': 'form-control'})

    def clean(self):
        chat = self.cleaned_data.get('chat')
        recipient = self.cleaned_data.get('recipient')
        if not chat and not recipient:
            raise forms.ValidationError(_('The recipient or chat must be defined'))
        return self.cleaned_data

    def get_organization_staff(self):
        """Return the list of current organization staff"""
        data = []
        for item in Vacancy.objects\
            .filter(department__organization=self.organization,
                    user__isnull=False):
            item_info = ', ' . join([item.name, item.user.get_full_name()])
            data.append((item.user.id, item_info))
        return data

    def clean_recipient(self):
        recipient_id = self.cleaned_data.get('recipient')
        if recipient_id:
            try:
                self.recipient = User.objects.get(id=recipient_id)
            except User.DoesNotExist:
                raise forms.ValidationError(_('There is no such User'))
        else:
            self.recipient = None
        return recipient_id

    def send(self):
        """Send the message by means of selected way"""
        cls = type(self)
        subject = self.cleaned_data.get('subject')
        content = self.cleaned_data.get('content')
        chat = self.cleaned_data.get('chat')
        if not self.chat and chat:
            self.chat = chat
        try:
            with transaction.atomic():
                # Create new message chat if it's necessary
                new_message_chat = MessageChat.objects.create(
                    subject=subject,
                    organization=self.organization,
                    recipient=self.recipient,
                    status=MessageChat.OPENED,
                    created_by=self.request.user,
                ) if not self.chat else self.chat

                # Create new message
                new_message = Message.objects.create(
                    subject=new_message_chat.subject,
                    status=Message.READY,
                    organization=self.organization,
                    sender=self.request.user,
                    recipient=self.recipient,
                    chat=new_message_chat,
                    content=content,
                )
                new_message_chat.participants.add(self.request.user)
                if self.recipient:
                    new_message_chat.participants.add(self.recipient)

                if self.request.FILES \
                    and 'attachment' in self.request.FILES:
                    for _attachment in self.request.FILES.getlist('attachment'):
                        new_message_attachment = MessageAttachment.objects\
                            .create(
                                file=handle_uploaded_file(_attachment),
                                message=new_message,
                                created_by=self.request.user,
                                file_name=_attachment.name,
                                content_type=_attachment.content_type,
                            )
        except IntegrityError as exc:
            raise
        else:
            new_message.upload_files()

    def get_errors_msg(self):
        """
        Return the errors as one string.
        """
        errors = []
        for field_name, field_messages in self.errors.items():
            errors.append('{0} : {1}' \
                . format(field_name, ', ' \
                    . join(map(lambda x: strip_tags(x), field_messages)))
                )
        return '; ' . join(errors)

    def get_errors(self):
        """
        Return the errors as one string.
        """
        errors = {}
        for field_name, field_messages in self.errors.items():
            errors[field_name] = ', ' . join(
                map(lambda x: strip_tags(x), field_messages)
            )
        return errors

    def save(self, *args, **kwargs):
        pass


