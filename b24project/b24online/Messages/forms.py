# -*- encoding: utf-8 -*-

"""
Forms for `Message` application.
"""

import logging

from django.db import transaction, IntegrityError

from django import forms
from django.utils.translation import ugettext as _
from django.utils.html import strip_tags

from b24online.models import (User, Organization, MessageChat,
                              Message, MessageAttachment)
from b24online.utils import handle_uploaded_file
from django.core.mail import EmailMessage
from b24online import InvalidParametersError

logger = logging.getLogger(__name__)


class MessageForm(forms.ModelForm):

    AS_EMAIL, AS_MESSAGE = 'email', 'message'
    DELIVERY_WAYS = (
        (AS_EMAIL, _('As email')),
        (AS_MESSAGE, _('As message')),
    )

    delivery_way = forms.ChoiceField(label=_('Delivery way'),
                                     choices=DELIVERY_WAYS, required=True)
    chat = forms.ModelChoiceField(queryset=MessageChat.objects.all(),
                                  required=False)
    attachment = forms.FileField(label=_('Message attachment'), required=False)
    is_private = forms.BooleanField(required=False)

    class Meta:
        model = Message
        fields = ('organization', 'recipient', 'subject', 'content')

    def __init__(self, request, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        self.request = request
        self.initial['delivery_way'] = type(self).AS_MESSAGE
        self.initial['is_private'] = False
        self.fields['content'].required = True

    def send(self):
        """
        Send the message by means of selected way.
        """
        cls = type(self)
        organization = self.cleaned_data.get('organization')
        recipient = self.cleaned_data.get('recipient')
        subject = self.cleaned_data.get('subject')
        content = self.cleaned_data.get('content')
        delivery_way = self.cleaned_data.get('delivery_way')
        is_private = self.cleaned_data.get('is_private')
        chat = self.cleaned_data.get('chat')
        if delivery_way == cls.AS_MESSAGE:
            try:
                with transaction.atomic():
                    new_message_chat = MessageChat.objects.create(
                        subject=subject,
                        organization=organization,
                        status=MessageChat.OPENED,
                        is_private=is_private,
                        created_by=self.request.user,
                    ) if not chat else chat
                    new_message = Message.objects.create(
                        subject=new_message_chat.subject,
                        status=Message.READY,
                        recipient=recipient,
                        organization=organization,
                        sender=self.request.user,
                        chat=new_message_chat,
                        content=content,
                    )
                    new_message_chat.participants.add(self.request.user)
                    if recipient:
                        new_message_chat.participants.add(recipient)

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
                
        else:
            if not organization.email:
                email = 'admin@tppcenter.com'
                subject = _('This message was sent to '
                    'company with id = %(organization_id)d, '
                    'subject: %(subject)s') % \
                    {'organization_id': organization.id,
                     'subject': subject}
            else:
                email = organization.email
                subject = _('New message: %(subject)s') % {'subject': subject}

            mail = EmailMessage(
                subject,
                content,
                getattr(settings, 'DEFAULT_FROM_EMAIL',
                        'noreply@tppcenter.com'),
                [email,]
            )
            if attachment:
                mail.attach(attachment.name, attachment.read(),
                            attachment.content_type)
            mail.send()

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


# FIXME: Make a one form from two
class MessageSendForm(forms.ModelForm):

    chat = forms.ModelChoiceField(
        queryset=MessageChat.objects.all(),
        required=False
    )
    attachment = forms.FileField(
        label=_('Message attachment'),
        required=False,
    )
    is_private = forms.BooleanField(
        required=False
    )
    send_as_message = forms.BooleanField(
        label=_('Send as message'),
        required=False
    )
    send_as_email = forms.BooleanField(
        label=_('Send as email'),
        required=False
    )
    redirect_to_chat = forms.BooleanField(
        label=_('Redirect to new chat right now?'),
        required=False
    )

    class Meta:
        model = Message
        fields = ('organization', 'recipient', 'subject', 'content')

    def __init__(self, request, *args, **kwargs):
        cls = type(self)
        # Extract the parameters for recipient instance
        self.recipient_type = kwargs.pop('recipient_type', None)
        item_id = kwargs.pop('item_id', None)

        # Prepare the form
        super(MessageSendForm, self).__init__(*args, **kwargs)
        self.request = request
        self.initial['is_private'] = False
        self.fields['content'].required = True
        self.fields['attachment'].widget.attrs.update(
            {'class': 'file-attachment'}
        )
        self.initial['send_as_message'] = True
        self.initial['redirect_to_chat'] = True

        # Process the recipinet if it is defined
        if self.recipient_type == 'user':
            try:
                self.item = User.objects.get(pk=item_id)
            except User.DoesNotExist:
                raise InvalidParametersError(
                    _('Invalid parameters. There is not such user')
                )
            else:
                del self.fields['organization']
                del self.fields['recipient']
        elif self.recipient_type == 'organization':
            try:
                self.item = Organization.objects.get(pk=item_id)
            except Organization.DoesNotExist:
                raise InvalidParametersError(
                    _('Invalid parameters. There is not such organization')
                )
            else:
                del self.fields['organization']
                user_ids = [vacancy.user.pk for vacancy in \
                            self.item.vacancies if vacancy.user]
                self.fields['recipient'] = forms.ModelChoiceField(
                    label=_('For user'),
                    queryset=User.objects.filter(
                    pk__in=user_ids),
                    required=False,
                )
                if not user_ids:
                    self.fields['recipient'].label += \
                        ', (' + _('the organization staff is empty') + ')'
                    self.fields['recipient']\
                        .widget.attrs['disabled'] = 'disabled'
                    self.initial['send_as_message'] = False
                    self.initial['send_as_email'] = True
                    self.fields['send_as_message']\
                        .widget.attrs['disabled'] = 'disabled'
                    self.fields['send_as_email']\
                        .widget.attrs['disabled'] = 'disabled'

    def for_organization(self):
        return self.recipient_type == 'organization'

    def send(self):
        """
        Send the message by means of selected way.
        """
        cls = type(self)

        if self.recipient_type == 'organization' and \
            self.item and isinstance(self.item, Organization):
            organization = self.item
        elif self.recipient_type == 'user' and self.item:
            organization = None
        else:
            organization = self.cleaned_data.get('organization')

        if self.recipient_type == 'user' and \
            self.item and isinstance(self.item, User):
            recipient = self.item
        else:
            recipient = self.cleaned_data.get('recipient')

        subject = self.cleaned_data.get('subject')
        content = self.cleaned_data.get('content')
        is_private = self.cleaned_data.get('is_private')
        chat = self.cleaned_data.get('chat')
        send_as_message = self.cleaned_data.get('send_as_message')
        send_as_email = self.cleaned_data.get('send_as_email')
        if send_as_message:
            try:
                with transaction.atomic():
                    self.new_message_chat = MessageChat.objects.create(
                        subject=subject,
                        organization=organization,
                        recipient=recipient,
                        status=MessageChat.OPENED,
                        is_private=is_private,
                        created_by=self.request.user,
                    ) if not chat else chat
                    new_message = Message.objects.create(
                        subject=self.new_message_chat.subject,
                        status=Message.READY,
                        recipient=recipient,
                        organization=organization,
                        sender=self.request.user,
                        chat=self.new_message_chat,
                        content=content,
                    )
                    self.new_message_chat.participants.add(self.request.user)
                    if recipient:
                        self.new_message_chat.participants.add(recipient)

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

        if send_as_email and organization:
            if not organization.email:
                email = 'admin@tppcenter.com'
                subject = _('This message was sent to '
                    'company with id = %(organization_id)d, '
                    'subject: %(subject)s') % \
                    {'organization_id': organization.id,
                     'subject': subject}
            else:
                email = organization.email
                subject = _('New message: %(subject)s') % {'subject': subject}

            mail = EmailMessage(
                subject,
                content,
                getattr(settings, 'DEFAULT_FROM_EMAIL',
                        'noreply@tppcenter.com'),
                [email,]
            )
            if attachment:
                mail.attach(attachment.name, attachment.read(),
                            attachment.content_type)
            mail.send()

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


class AddParticipantForm(forms.Form):

    new_user = forms.ModelChoiceField(
        label=_('Add user to chat'),
        queryset=User.objects.all(),
        required=True,
    )

    def __init__(self, request, item_id, *args, **kwargs):
        super(AddParticipantForm, self).__init__(*args, **kwargs)
        self.request = request
        try:
            self.chat = MessageChat.objects.get(pk=item_id)
        except MessageChat.DoesNotExist:
            self.chat = None

    def save(self):
        new_user = self.cleaned_data.get('new_user')
        if new_user:
            self.chat.participants.add(new_user)
        

class UpdateChatForm(forms.Form):

    subject = forms.CharField(
        label=_('Chat subject'),
        required=True,
    )

    close_chat = forms.BooleanField(
        label=_('Close chat'),
        required=False,
        help_text=_('Only chat\'s creator has the permission'
                    ' to close the chat')
    )

    def __init__(self, request, item_id, *args, **kwargs):
        super(UpdateChatForm, self).__init__(*args, **kwargs)
        self.request = request
        try:
            self.chat = MessageChat.objects.get(pk=item_id)
        except MessageChat.DoesNotExist:
            self.chat = None
        self.initial['subject'] = self.chat.subject
        if not self.can_close():
            del self.fields['close_chat']
           
    def can_close(self):
        return self.request.user == self.chat.created_by
        
    def save(self):
        subject = self.cleaned_data.get('subject')
        if subject:
            self.chat.subject = subject
        if self.can_close() and self.cleaned_data.get('close_chat'):
            self.chat.status = MessageChat.CLOSED
        self.chat.save()
