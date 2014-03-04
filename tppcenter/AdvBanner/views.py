__author__ = 'user'
from appl.models import AdvBannerType, AdvBanner, Cabinet
from core.models import Item
from django.shortcuts import HttpResponse, render_to_response
from appl.models import *
from django.db.models import ObjectDoesNotExist
from appl import func
from django.template import RequestContext, loader
from django.utils.translation import ugettext as _

@login_required(login_url='/login/')
def gatPositions(request):

    bannerType = AdvBannerType.objects.all().values('pk', 'sites__name')

    bannerType_ids = [btype['pk'] for btype in bannerType]
    bannerNames = Item.getItemsAttributesValues('NAME', bannerType_ids)
    sites = {}

    for btype in bannerType:

        if btype['sites__name'] not in sites:
            sites[btype['sites__name']] = {}

        if btype['pk'] in bannerNames:
            sites[btype['sites__name']][btype['pk']] = bannerNames[btype['pk']]

    cabinet = Cabinet.objects.get(user=request.user)
    cabinetAttr = cabinet.getAttributeValues(('USER_FIRST_NAME', 'USER_MIDDLE_NAME', 'USER_LAST_NAME'))

    user_name = ''

    if len(cabinetAttr) != 0:
        user_name = cabinetAttr.get('USER_FIRST_NAME', [''])[0] + ' ' + cabinetAttr.get('USER_MIDDLE_NAME', [''])[0] + ' '\
                    + cabinetAttr.get('USER_LAST_NAME', [''])[0]

    current_section = _('Banners')


    notification = Notification.objects.filter(user=request.user, read=False).count()


    templateParams = {
        'sites': sites,
        'user_name': user_name,
        'current_section': current_section,
        'notification': notification,
    }

    return render_to_response("AdvBanner/index.html", templateParams, context_instance=RequestContext(request))

def bannerForm(request, bannerType):

    cabinet = Cabinet.objects.get(user=request.user)
    cabinetAttr = cabinet.getAttributeValues(('USER_FIRST_NAME', 'USER_MIDDLE_NAME', 'USER_LAST_NAME'))

    user_name = ''

    if len(cabinetAttr) != 0:
        user_name = cabinetAttr.get('USER_FIRST_NAME', [''])[0] + ' ' + cabinetAttr.get('USER_MIDDLE_NAME', ['']) + ' '\
                    + cabinetAttr.get('USER_LAST_NAME', [''])[0]


    notification = Notification.objects.filter(user=request.user, read=False).count()

    current_section = _('Banners')

    templateParams = {
        'user_name': user_name,
        'current_section': current_section,
        'notification': notification,
    }

    return render_to_response("AdvBanner/detail.html", templateParams, context_instance=RequestContext(request))