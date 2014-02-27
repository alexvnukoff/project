__author__ = 'user'
from django.shortcuts import render_to_response
from appl.models import *
from django.template import RequestContext
from django.core.paginator import Paginator
from appl import func

def viewMessages(request, item_id=None):

    page = request.GET.get('page', 1)

    user = request.user
    cabinet = Cabinet.objects.get(user=user).pk

    users = Messages.objects.filter(c2p__parent_id=cabinet).values_list('create_user', flat=True).distinct()

    users = Cabinet.objects.filter(Q(user__in=users) | Q(user=request.user.pk))
    users = func.sortQuerySetByAttr(users, 'USER_LAST_NAME', 'str').values('pk', 'user')
    userCabinet = {}

    for dict in users:
        if item_id is None and dict['user'] != request.user.pk:
            item_id = dict['pk']

        userCabinet[dict['user']] = dict['pk']

    users = Item.getItemsAttributesValues(('USER_LAST_NAME', 'USER_FIRST_NAME', 'USER_MIDDLE_NAME', 'IMAGE'), user_ids)

    messages = Messages.objects.filter(c2p__parent_id=item_id).order_by('-create_date')
    paginator = Paginator(messages, 10)
    messages = paginator.page(page).object_list

    massages_id = [mess.pk for mess in messages]
    messages_attr = Item.getItemsAttributesValues('DETAIL_TEXT', massages_id)

    for mess in messages:
        user = userCabinet[mess.create_user.pk]
        messages_attr[mess.pk].update(users[user])
        messages_attr[mess.pk]['CREATE_DATE'] = mess.create_date

    del users[request.user.pk]


    notification = len(Notification.objects.filter(user=request.user, read=False))

    if not user.first_name and not user.last_name:
        user_name = user.email
    else:
        user_name = user.first_name + ' ' + user.last_name

    templateParams = {
        'user_name': user_name,
        'current_section': '',
        'notification': notification,
        'messages': messages_attr,
        'users': users,
        'active': item_id
    }

    return render_to_response("Messages/index.html", templateParams, context_instance=RequestContext(request))