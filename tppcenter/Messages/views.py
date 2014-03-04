__author__ = 'user'
from django.shortcuts import render_to_response, HttpResponse
from appl.models import *
from django.db.models import Max, ObjectDoesNotExist
from appl import func
from django.template import RequestContext, loader
from django.utils.translation import trans_real
from collections import OrderedDict

@login_required(login_url='/login/')
def viewMessages(request, item_id=None):

    if not request.is_ajax():
        cabinet = Cabinet.objects.get(user=request.user).pk

        user_name = ''

        contacts = _getContactList(request, cabinet, item_id)

        cabinets = {}
        organizations = {}


        if contacts is not False:

            cabinets, organizations, item_id = contacts

            if item_id:
                messages = _getMessageList(request, item_id, 1)
            else:
                messages = ''

        else:
            messages = ''


        if cabinet in cabinets:
            user_name = cabinets[cabinet].get('USER_FIRST_NAME', [''])[0]
            user_name += ' ' + cabinets[cabinet].get('USER_LAST_NAME', [''])[0]

            del cabinets[cabinet]


        notification = Notification.objects.filter(user=request.user, read=False).count()

        templateParams = {
            'user_name': user_name,
            'current_section': '',
            'notification': notification,
            'messages': messages,
            'cabinets': cabinets,
            'organizations': organizations,
            'active': item_id
        }

        return render_to_response("Messages/index.html", templateParams, context_instance=RequestContext(request))
    else:

        if item_id is None:
            raise ValueError('Receiver is not provided')

        date = request.GET.get('date', 0)
        lid = request.GET.get('lid', 0)
        box = request.GET.get('box', None)
        page = request.GET.get('page', 1)

        if box is None:
            return HttpResponse(_getMessageList(request, item_id, page, date, lid))
        else:
            messages = _getMessageList(request, item_id, page)

            templateParams = {
                'active': item_id,
                'messages': messages
            }

            return render_to_response("Messages/contentBox.html", templateParams, context_instance=RequestContext(request))

def _getMessageList(request, item_id, page, date=None, lid=None):
    from collections import OrderedDict
    from django.utils.dateparse import parse_datetime

    user = request.user
    cabinet_my = Cabinet.objects.get(user=user)

    try:
        item = Item.objects.get(pk=item_id)
    except ObjectDoesNotExist:
        item = None

    templateParams = {}

    if item:
        attrs = ('USER_LAST_NAME', 'USER_FIRST_NAME', 'USER_MIDDLE_NAME', 'IMAGE', 'NAME')
        users = Item.getItemsAttributesValues(attrs, [item.pk, cabinet_my.pk])

        messages = Messages.objects.filter(c2p__parent=item.pk)
        messages = messages.filter(c2p__parent=cabinet_my.pk).order_by('-create_date')

        if date is not None and lid is not None:

            if date != 0:
                date = parse_datetime(date)
            lid = int(lid)

            if page == 1:
                messages = messages.filter(pk__gt=lid)
                templateParams['lastDate'] = date
            else:
                templateParams['startDate'] = date
                messages = messages.filter(pk__lt=lid)

        trans_real.activate('en')
        result = func.setPaginationForSearchWithValues(messages, *('DETAIL_TEXT',), page_num=10, page=1)
        trans_real.deactivate()
        messagesList = result[0]
        paginator = result[1]

        for mess in paginator.object_list:
            if mess.create_user == cabinet_my.user:
                user = cabinet_my.pk
            else:
                user = item.pk

            messagesList[mess.pk].update(users[user])
            messagesList[mess.pk]['CREATE_DATE'] = mess.create_date

        messagesList=OrderedDict(reversed(list(messagesList.items())))
    else:
        messagesList = {}

    template = loader.get_template('Messages/messagesPage.html')

    templateParams['messagesList'] = messagesList

    context = RequestContext(request, templateParams)

    return template.render(context)

def _getContactList(request, cabinet, item_id):

        mess = Messages.objects.filter(c2p__parent=cabinet)

        chats = Relationship.objects.filter(child=mess).exclude(parent=cabinet).values_list('parent', flat=True)\
            .annotate(Max('child__create_date')).order_by('-child__create_date__max')

        attrs = ('USER_LAST_NAME', 'USER_FIRST_NAME', 'USER_MIDDLE_NAME', 'IMAGE', 'NAME')

        chatsList = list(chats)

        if item_id is not None:
            item_id = int(item_id)
            chatsList.insert(0, item_id)

        org = Organization.objects.filter(pk__in=chatsList).values_list('pk', flat=True)
        users = Cabinet.objects.filter(pk__in=chatsList).values_list('pk', flat=True)

        if cabinet == item_id or (item_id not in org and item_id not in users):
            item_id = None

        if len(users) > 0 or len(org) > 0 or item_id is not None:

            chats = [chat for chat in chats if chat in users or chat in org]

            if item_id is None:
                item_id = chats[0]
            else:
                chats.insert(0, item_id)

            chats.append(cabinet)

            organizations = OrderedDict()
            cabinets = OrderedDict()

            chats = Item.getItemsAttributesValues(attrs, chats)

            for id, chat in chats.items():
                if id in org:
                    organizations[id] = chat
                else:
                    cabinets[id] = chat

            return cabinets, organizations, item_id


        return False

@login_required(login_url='/login/')
def addMessages(request):
    #TODO: Artur limit of chars for message
    item_id = int(request.POST.get('active'))
    text = request.POST.get('text')

    if len(text) == 0:
        raise ValueError('Empty message')

    message = Messages(create_user=request.user)
    message.save()

    trans_real.activate('en')
    message.setAttributeValue({'DETAIL_TEXT': text}, request.user)
    trans_real.deactivate()

    cabinet_my = Cabinet.objects.get(user=request.user)

    notify = None

    try:
        item = Cabinet.objects.get(pk=item_id)
        notify = item.user.pk
    except ObjectDoesNotExist:
        item = Organization.objects.get(pk=item_id)


    Relationship.setRelRelationship(item, message, request.user)
    Relationship.setRelRelationship(cabinet_my, message, request.user, 'dependence')


    if notify:
        func.sendTask('private_massage', user=notify, fromUser=cabinet_my.pk)

    return HttpResponse('')







