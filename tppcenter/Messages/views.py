__author__ = 'user'
from django.shortcuts import render_to_response, HttpResponse
from appl.models import *
from django.db.models import Max, ObjectDoesNotExist
from appl import func
from django.template import RequestContext, loader
from django.utils.translation import trans_real
from collections import OrderedDict
from django.utils.translation import gettext as _
from django.utils.dateparse import parse_datetime
from copy import copy

@login_required(login_url='/login/')
def viewMessages(request, recipient=None):
    '''
        recipient - cabinet id / org id of the message recipient
    '''

    # who is the sender ?
    current_company = request.session.get('current_company', False)

    #TODO: Delete for full usability
    current_company = False

    if current_company is False:
        senderObj = Cabinet.objects.get(user=request.user)
    else:
        senderObj = Organization.objects.get(pk=current_company)

    sender = senderObj.pk

    if recipient is not None:

        if recipient == sender:
            recipient = None

        elif not Organization.objects.filter(pk=recipient).exists() and not Cabinet.objects.filter(pk=recipient).exists():
            recipient = None
        else:
            recipient = int(recipient)

    if not request.is_ajax():
        #Messages page just opened, not chatting yet
        contacts = _getContactList(request, sender, recipient)

        cabinets = {}
        organizations = {}

        if contacts is not False:

            senderWithAttr, cabinets, organizations, recipientWithAttr = contacts

            if not isinstance(senderWithAttr, dict):
                senderWithAttr = {}

            if not isinstance(recipientWithAttr, dict):
                recipientWithAttr = {}

            senderWithAttr['PK'] = sender
            recipientWithAttr['PK'] = recipient

            if recipient:
                messages = _getMessageList(request, recipientWithAttr, senderWithAttr)
            else:
                messages = ''

        else:
            messages = ''

        templateParams = {
            'messages': messages,
            'cabinets': cabinets,
            'organizations': organizations,
            'active': recipient,
            'current_section': _('Private messages')
        }

        return render_to_response("Messages/index.html", templateParams, context_instance=RequestContext(request))
    else:

        if recipient is None:
            raise ValueError('Receiver is not provided')

        date = request.GET.get('date', 0)
        lid = request.GET.get('lid', 0)
        box = request.GET.get('box', None)

        if box is None:
            return HttpResponse(_getMessageList(request, recipient, sender, date, lid))
        else:
            messages = _getMessageList(request, recipient, sender)

            templateParams = {
                'active': recipient,
                'messages': messages
            }

            return render_to_response("Messages/contentBox.html", templateParams, context_instance=RequestContext(request))

def _getMessageList(request, recipient, sender,  date=None, lid=None):
    '''
        recipient - cabinet pk / org pk
        sender - cabinet pk / org pk  - it's me
    '''

    itemsWithAttrs = {}

    if isinstance(recipient, dict) and isinstance(sender, dict):
        itemsWithAttrs[recipient['PK']] = copy(recipient)
        recipient = recipient['PK']

        itemsWithAttrs[sender['PK']] = copy(sender)
        sender = sender['PK']
    else:
        attrs = ('USER_LAST_NAME', 'USER_FIRST_NAME', 'USER_MIDDLE_NAME', 'IMAGE', 'NAME')
        itemsWithAttrs = Item.getItemsAttributesValues(attrs, [recipient, sender])

    templateParams = {}

    messages = Messages.objects.filter(c2p__parent=recipient)
    messages = messages.filter(c2p__parent=sender)

    if date is not None and lid is not None:

        if date != 0:
            date = parse_datetime(date)

        try:
            lid = int(lid)
        except ValueError:
            lid = 0

        type = request.POST.get('type', False)

        if type == 'scroll':
            #get older messages
            templateParams['startDate'] = date
            messages = messages.filter(pk__lt=lid)

        else:
            messages = messages.filter(pk__gt=lid)
            templateParams['lastDate'] = date


    messages = messages.order_by('-create_date').values_list('pk', flat=True)[:10]
    messages = list(messages)

    owners = Relationship.objects.filter(child__in=messages, type="dependence").values('parent', 'child')

    ownerDict = {}

    for owner in owners:
        ownerDict[owner['child']] = itemsWithAttrs[owner['parent']]

    #There is no multilingual messages
    trans_real.activate('en')
    messagesList = Item.getItemsAttributesValues('DETAIL_TEXT', messages)
    trans_real.deactivate()

    for messageID in messagesList.keys():
        messagesList[messageID]['OWNER'] = ownerDict[messageID]

    #get latest messages ordered from new to older
    messagesList=OrderedDict(reversed(list(messagesList.items())))

    template = loader.get_template('Messages/messagesPage.html')

    templateParams['messagesList'] = messagesList

    context = RequestContext(request, templateParams)

    return template.render(context)

def _getContactList(request, sender, recipient):
    '''
        get contact list of the sender, ordered by latest chat
    '''

    #All messages that related to sender
    mess = Messages.objects.filter(c2p__parent=sender)

    #Get all people who chatted with the sender and sort the last messages with everyone by date
    chats = Relationship.objects.filter(child=mess).exclude(parent=sender).values_list('parent', flat=True)\
        .annotate(Max('child__create_date')).order_by('-child__create_date__max')

    chatsList = list(chats)


    if recipient is not None:
        # some recipient selected ?
        recipient = int(recipient)
        chatsList.insert(0, recipient)

    #Get all recipients include the new one whe selected
    org = Organization.objects.filter(pk__in=chatsList).values_list('pk', flat=True)
    cabinets = Cabinet.objects.filter(pk__in=chatsList).values_list('pk', flat=True)

    if len(cabinets) > 0 or len(org) > 0 or recipient is not None:
        #Some chat selected if we have one or the new recipient is valid

        chats = [chat for chat in chatsList if chat in cabinets or chat in org]

        if recipient is None:
            recipient = chats[0]
        else:
            chats.insert(0, recipient)

        chats.append(sender)

        organizations = OrderedDict()
        cabinets = OrderedDict()

        attrs = ('USER_LAST_NAME', 'USER_FIRST_NAME', 'USER_MIDDLE_NAME', 'IMAGE', 'NAME')
        chats = Item.getItemsAttributesValues(attrs, chats)

        for id, chat in chats.items():

            if sender == id:
                sender = chat
                continue
            elif id in org:
                organizations[id] = chat
            else:
                cabinets[id] = chat

            if recipient is not None and recipient == id:
                recipient = chat

        return sender, cabinets, organizations, recipient


    return False

@login_required(login_url='/login/')
def addMessages(request):

    # who is the sender ?
    current_company = request.session.get('current_company', False)

    #TODO: Delete for full usability
    current_company = False

    if current_company is False:
        sender = Cabinet.objects.get(user=request.user)
    else:
        sender = Organization.objects.get(pk=current_company)


    #TODO: Artur limit of chars for message
    recipient = int(request.POST.get('active'))
    text = request.POST.get('text')

    if len(text) == 0:
        raise ValueError('Empty message')

    # create message
    message = Messages(create_user=request.user)
    message.save()

    # create message text, only one standard language
    trans_real.activate('en')
    message.setAttributeValue({'DETAIL_TEXT': text}, request.user)
    trans_real.deactivate()

    notify = None

    try:
        recipient = Cabinet.objects.get(pk=recipient)
    except ObjectDoesNotExist:
        recipient = Organization.objects.get(pk=recipient)


    Relationship.setRelRelationship(recipient, message, request.user)
    Relationship.setRelRelationship(sender, message, request.user, 'dependence')


    if notify:
        func.sendTask('private_massage', recipient=recipient.pk, fromUser=sender.pk)

    return HttpResponse('')







