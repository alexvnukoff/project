# -*- encoding: utf-8 -*-

import json
import logging

from collections import OrderedDict

from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Q, Case, When, CharField, Max, Count
from django.template import RequestContext, loader
from django.template.loader import render_to_string
from django.shortcuts import render_to_response
from django.http import (HttpResponse, HttpResponseBadRequest, Http404, 
                         HttpResponseRedirect)
from django.utils.timezone import now
from django.utils.translation import gettext as _
from django.utils.dateparse import parse_datetime

from b24online import InvalidParametersError
from b24online.models import (Message, MessageChat, MessageAttachment)
from b24online.utils import deep_merge_dict, get_current_organization
from b24online.Messages.forms import (MessageForm, MessageSendForm, 
                                      AddParticipantForm, UpdateChatForm)

logger = logging.getLogger(__name__)

@login_required
def view_messages(request, recipient_id=None):
    if recipient_id is not None:
        if recipient_id == request.user.pk:
            recipient_id = None
        elif not get_user_model().objects.filter(pk=recipient_id).exists():
            recipient_id = None
        else:
            recipient_id = int(recipient_id)

    if not request.is_ajax():
        # Messages page just opened, not chatting yet
        contacts = _get_last_message_by_contact(request.user.pk, recipient_id)
        active = next(iter(contacts), None)

        template_params = {
            'messages': _get_message_list(request, active),
            'contacts': contacts,
            'active': active,
            'current_section': _('Private messages')
        }

        return render_to_response("b24online/Messages/index.html", template_params, context_instance=RequestContext(request))
    else:
        if recipient_id is None:
            raise ValueError('Receiver is not provided')

        date = request.GET.get('date', None)
        last_message_id = request.GET.get('lid', None)
        box = request.GET.get('box', None)

        if box is None:
            return HttpResponse(_get_message_list(request, recipient_id, date, last_message_id))
        else:
            messages = _get_message_list(request, recipient_id)

            template_params = {
                'active': recipient_id,
                'messages': messages
            }

            return render_to_response("b24online/Messages/contentBox.html", template_params,
                                      context_instance=RequestContext(request))


def _get_message_list(request, recipient_id, date=None, last_message_id=None):
    messages = None
    template_params = {}

    if date and last_message_id:
        date = parse_datetime(date)
        action_type = request.POST.get('type', False)

        if action_type == 'scroll':
            # get older messages
            template_params['startDate'] = date
        else:
            template_params['lastDate'] = date

        messages = Message.objects.filter(pk__gt=last_message_id).order_by('-created_at')[:10]
    elif recipient_id is not None:
        messages = Message.objects.filter(
            Q(recipient=request.user, sender=recipient_id) | Q(recipient=recipient_id, sender=request.user)) \
                       .order_by('-created_at')[:10]

    if messages is not None:
        Message.objects.filter(pk__in=messages).update(is_read=True)
        messages = reversed(list(messages))

    # # convert message's create_date to native date for user
    # base_dir = 'b24online/GeoIPCity.dat'  # database file with cities
    # dir = os.path.join(settings.MEDIA_ROOT, base_dir).replace('\\', '/')
    # gi = pygeoip.GeoIP(dir)
    #
    # # get user's IP
    # x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    #
    # if x_forwarded_for:
    #     ip = x_forwarded_for.split(',')[0]
    #     # for HAProxy balancer
    #     # ip = request.META.get('HTTP_X_REAL_IP', None)
    # else:
    #     ip = request.META.get('REMOTE_ADDR')
    #     # ip = '82.166.224.212' # IP for Jerusalem - just for debugging
    #
    # data = gi.record_by_addr(ip)
    # # receive timezone for User IP
    # if data is not None:
    #     tz = timezone(pygeoip.time_zone_by_country_and_region(data['country_code'], data['region_code']))
    # else:
    #     tz = timezone('UTC')
    #
    # for msg_id, msg_attr in messagesList.items():
    #     timestamp = msg_attr['CREATE_DATE'][0].timestamp()
    #     utc_dt = utc.localize(datetime.utcfromtimestamp(timestamp))
    #     msg_attr['CREATE_DATE'] = [utc_dt.astimezone(tz)]

    template_params['message_queryset'] = messages
    template = loader.get_template('b24online/Messages/messagesPage.html')
    context = RequestContext(request, template_params)
    return template.render(context)


def _get_last_message_by_contact(sender, recipient):
    """
        get contact list of the sender, ordered by latest chat
    """

    # Get all contact list(users) that ever contacted with the sender (current user)
    # to be able to group by sets of (sender, recipient) or (recipient, sender)
    # we are grouping only by the contact id, if sender == current user then set to group by recipient
    # and vise versa
    chats = Message.objects.filter(Q(sender=sender) | Q(recipient=sender)) \
                .annotate(user=Case(
                    When(sender_id=sender, then="recipient_id"), default="sender_id", output_field=CharField())
                ).values('user').annotate(sent_at=Max('created_at')).order_by('-sent_at')[:10]  # TODO paginate ?

    chats = dict((user["user"], user) for user in chats)

    if recipient and recipient not in chats.keys():
        # if the user that sender (current user or request.user) wants to contact with is not in contacts list
        # We will add him to contact list and fake the sent_date to be the first in the contact list
        chats[int(recipient)] = {'sent_at': now(), 'user': int(recipient)}

    # Get count of unread messages from those users
    unread = Message.objects.filter(sender__in=chats.keys(), is_read=False, recipient=sender).values('sender_id') \
        .annotate(unread=Count('pk'))
    unread = dict((user["sender_id"], user) for user in unread)

    # Get contacts data
    users = get_user_model().objects.filter(pk__in=chats.keys()).values('pk', 'profile__last_name', 'profile__first_name', 'email')
    users = dict((user["pk"], user) for user in users)

    # Merge all results to one dict
    result = deep_merge_dict(users, unread)
    result = deep_merge_dict(result, chats)

    # Sort dict by last message date and save the order with OrderedDict
    return OrderedDict(sorted(((k, v) for k, v in result.items()), key=lambda user: user[1]['sent_at'], reverse=True))


@login_required
def add_message(request, content=None, recipient_id=None):
    if recipient_id is None:
        recipient_id = int(request.POST.get('active'))
    if content is None:
        content = request.POST.get('text')

    if not content or len(content.strip()) == 0:
        return HttpResponse('')

    Message.add_message(content.strip(), request.user, recipient_id)

    return HttpResponse('')


@login_required
def view_chats(request):
    
    user = request.user
    current_organization = get_current_organization(request)
    per_page = 20
    chats = MessageChat.objects\
        .filter(Q(organization=current_organization) | \
                Q(participants__id__exact=user.id),
                status=MessageChat.OPENED)\
        .distinct()\
        .order_by('-updated_at')

    context = {
        'organization_chats': chats.filter(is_private=False)[:per_page],
        'user_chats': chats.filter(is_private=True)[:per_page],
    }
    logger.debug(context)
    return render_to_response("b24online/Messages/chats.html",
        context, context_instance=RequestContext(request))


@login_required
def chat_messages(request, item_id):
    try:
        chat = MessageChat.objects.get(id=item_id)
    except MessageChat.DoesNotExist:
        raise Http404(_('There is not such message chat'))
    else:
        context = {
            'chat': chat,
            'messages': chat.chat_messages.order_by('created_at')
        }
        return render_to_response("b24online/Messages/chatMessages.html",
            context, context_instance=RequestContext(request))


@login_required
def add_to_chat(request):
    response_code = 'error'
    response_text = 'Error'
    if request.method == 'POST':
        form = MessageForm(request, data=request.POST, files=request.FILES)
        if form.is_valid():
            try:
                form.send()
            except IntegrityError as exc:
                response_text = _('Error during data saving') + str(exc)
            else:
                response_code = 'success'
                response_text = _('You have successfully sent the message')
        else:
            response_text = form.get_errors()
        return HttpResponse(
            json.dumps({'code': response_code, 'message': response_text}),
            content_type='application/json'
        )
    return HttpResponseBadRequest()


@login_required
def send_message(request, recipient_type, item_id, **kwargs):
    """
    Send the message to organization's or user's chats.
    """
    template_name = 'b24online/Messages/sendMessage.html'
    if request.is_ajax():
        data = {}
        if request.method == 'POST':
            form = MessageSendForm(
                request,
                recipient_type=recipient_type,
                item_id=item_id,
                data=request.POST,
                files=request.FILES
            )
            if form.is_valid():
                try:
                    form.send()
                except IntegrityError as err:
                    data.update({
                        'code': 'critical',
                        'msg': _('Error during data saving: {0}') \
                            .format(exc)
                    })
                else:
                    data.update({
                        'code': 'success',
                        'msg': _('You have successfully sent the message'),
                    })
                    if form.cleaned_data.get('redirect_to_chat'):
                        data['redirect_to_chat'] = reverse('messages:main')
            else:
                data.update({
                    'code': 'error',
                    'errors': form.get_errors(),
                    'msg': _('There are some errors'),
                })
        else:
            try:
                form = MessageSendForm(
                    request,
                    recipient_type=recipient_type,
                    item_id=item_id
                )
            except InvalidParametersError as err:
                data.update({
                    'code': 'critical',
                    'msg': render_to_string(
                        template_name,
                        {'error': 'ERROR: {0}' . format(err)},
                        context_instance=RequestContext(request),
                    ),
                })
            else:
                data.update({
                    'code': 'success',
                    'msg': render_to_string(
                        template_name,
                        {'form': form, 'request': request},
                        context_instance=RequestContext(request),
                    )
                })
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponseBadRequest()


@login_required
def add_participant(request, item_id, **kwargs):
    template_name = 'b24online/Messages/addParticipant.html'
    if request.is_ajax():
        data = {}
        if request.method == 'POST':
            form = AddParticipantForm(
                request, 
                item_id=item_id,
                data=request.POST,
                files=request.FILES
            )
            if form.is_valid():
                form.save()
                data.update({
                    'code': 'success',
                    'msg': _('You have successfully add new participant'),
                })
            else:
                data.update({
                    'code': 'error',
                    'errors': form.get_errors(),
                    'msg': _('There are some errors'),
                })
        else:
            form = AddParticipantForm(request, item_id=item_id)
            data.update({
                'code': 'success',
                'msg': render_to_string(
                    template_name,
                    {'form': form, 'request': request},
                    context_instance=RequestContext(request),
                )
            })
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponseBadRequest()
    

    

@login_required
def update_chat(request, item_id, **kwargs):
    template_name = 'b24online/Messages/updateChat.html'
    if request.is_ajax():
        data = {}
        if request.method == 'POST':
            form = UpdateChatForm(
                request, 
                item_id=item_id,
                data=request.POST,
                files=request.FILES
            )
            if form.is_valid():
                form.save()
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
        else:
            form = UpdateChatForm(request, item_id=item_id)
            data.update({
                'code': 'success',
                'msg': render_to_string(
                    template_name,
                    {'form': form, 'request': request},
                    context_instance=RequestContext(request),
                )
            })
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponseBadRequest()
    
    
@login_required
def leave_chat(request, item_id, **kwargs):
    try:
        chat = MessageChat.objects.get(pk=item_id)
    except MessageChat.DoesNotExist:
        pass
    else:
        chat.participants.remove(request.user)
    return HttpResponseRedirect(reverse('messages:main'))
