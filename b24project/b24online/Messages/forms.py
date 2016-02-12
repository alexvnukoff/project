# -*- encoding: utf-8 -*-

"""
Forms for `Message` application.
"""

import logging

from django.db import IntegrityError
from django import forms
from django.utils.translation import ugettext as _

from b24online.models import Message

logger = logging.getLogger(__name__)


class MessageForm(forms.ModelForm):

    AS_EMAIL, AS_MESSAGE = 'email', 'message'
    DELIVERY_WAYS = (
        (AS_EMAIL, _('As email')),
        (AS_MESSAGE, _('As message')),
    ) 

    delivery_way = forms.ChoiceField(
        label=_('Delivery way'), 
        choices=DELIVERY_WAYS,
        required=True,
    )

    class Meta:
        model = Message
        fields = ('organization', 'recipient', 'subject', 'content')

    def __init__(self, request, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        self.request = request
        self.initial['delivery_way'] = type(self).AS_MESSAGE

    def send(self):
        """
        Send the message.
        """
        cls = type(self)
        data = self.cleaned_data
        organization = data.get('organization')
        recipient = data.get('recipient')
        subject = data.get('subject', ''),
        content = data.get('content')
        delivery_way = data.get('delivery_way')
        if delivery_way == cls.AS_MESSAGE:
            try:
                with transaction.atomic():
                    new_message_chat = MessageChat.objects.create(
                        subject=subject,
                        status=MessageChat.OPENED,
                    )
                    new_message_chat.participants.add(self.request.user)
                    new_message = Message.objects.create(
                        subject=subject,
                        status=Message.READY,
                        created_by=self.request.user,
                        recipient=recipient,
                        organization=organization,
                        sender=self.request.user,
                        chat=new_message_chat,
                    )
            except IntegrationError:
                raise
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


    def save(self, *args, **kwargs):
        pass
