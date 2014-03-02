__author__ = 'user'
from django.shortcuts import render_to_response, HttpResponse
from appl.models import *
from django.db.models import Max
from appl import func
from django.template import RequestContext, loader

def viewMessages(request, item_id=None):

    if not request.is_ajax():
        cabinet = Cabinet.objects.get(user=request.user).pk

        mess = Messages.objects.filter(c2p__parent=cabinet)
        users = Relationship.objects.filter(child=mess).exclude(parent=cabinet).values_list('parent', flat=True)\
            .annotate(Max('child__create_date')).order_by('-child__create_date__max')

        attrs = ('USER_LAST_NAME', 'USER_FIRST_NAME', 'USER_MIDDLE_NAME', 'IMAGE')
        user_name = ''

        if item_id is not None:
            item_id = int(item_id)
            cabinet_coll = Cabinet.objects.filter(pk=item_id)

            if not cabinet_coll.exists():
                item_id = None

        if len(users) > 0 or item_id is not None:

            users = list(users)

            if item_id is None:
                item_id = users[0]
            else:
                users.insert(0, item_id)

            users.append(cabinet)

            messages = _getMessageList(request, item_id, 1)

            users = Item.getItemsAttributesValues(attrs, users)

        else:
            users = Item.getItemsAttributesValues(attrs, [cabinet])
            messages = ''


        if cabinet in users:
            user_name = users[cabinet].get('USER_FIRST_NAME', [''])[0]
            user_name += ' ' + users[cabinet].get('USER_LAST_NAME', [''])[0]

            del users[cabinet]


        notification = Notification.objects.filter(user=request.user, read=False).count()

        templateParams = {
            'user_name': user_name,
            'current_section': '',
            'notification': notification,
            'messages': messages,
            'users': users,
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
    cabinets = Cabinet.objects.filter(Q(user=user) | Q(pk=item_id))
    templateParams = {}

    if len(cabinets) == 2:
        cabinetIds = [cabinet.pk for cabinet in cabinets]
        cabinet_my = cabinets.get(user=user)
        cabinet_coll = cabinets.get(pk=item_id)

        attrs = ('USER_LAST_NAME', 'USER_FIRST_NAME', 'USER_MIDDLE_NAME', 'IMAGE')
        users = Item.getItemsAttributesValues(attrs, cabinetIds)

        messages = Messages.objects.filter(c2p__parent=item_id)
        messages = messages.filter(c2p__parent=cabinet_my).order_by('-create_date')

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

        result = func.setPaginationForSearchWithValues(messages, *('DETAIL_TEXT',), page_num=10, page=1)
        messagesList = result[0]
        paginator = result[1]

        for mess in paginator.object_list:
            if mess.create_user == cabinet_my.user:
                user = cabinet_my.pk
            else:
                user = cabinet_coll.pk

            messagesList[mess.pk].update(users[user])
            messagesList[mess.pk]['CREATE_DATE'] = mess.create_date

        messagesList=OrderedDict(reversed(list(messagesList.items())))
    else:
        messagesList = {}

    template = loader.get_template('Messages/messagesPage.html')

    templateParams['messagesList'] = messagesList

    context = RequestContext(request, templateParams)

    return template.render(context)

def addMessages(request):

    item_id = int(request.POST.get('active'))
    text = request.POST.get('text')

    if len(text) == 0:
        raise ValueError('Empty message')

    message = Messages(create_user=request.user)
    message.save()
    message.setAttributeValue({'DETAIL_TEXT': text}, request.user)

    cabinet = Cabinet.objects.filter(Q(pk=item_id) | Q(user=request.user))

    if len(cabinet) != 2:
        raise ValueError('Cabinet does not exists')

    for cab in cabinet:
        if cab.pk == item_id:
            cabinet_coll = cab
        else:
            cabinet_my = cab


    Relationship.setRelRelationship(cabinet_coll, message, request.user)
    Relationship.setRelRelationship(cabinet_my, message, request.user, 'dependence')

    func.sendTask('private_massage', user=cabinet_coll.user.pk, fromUser=cabinet_my.pk)

    return HttpResponse('')