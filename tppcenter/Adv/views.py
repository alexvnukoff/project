from django.core.paginator import Paginator
from appl.models import AdvertisementItem, Organization
from appl import func
from core.models import Relationship, Item
from django.utils.timezone import now
from django.utils.translation import gettext as _
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from dateutil.parser import parse

def basket(request, page=1):

    current_company = request.session.get('current_company', False)

    if not request.session.get('current_company', False):
         return func.emptyCompany()

    item = Organization.objects.get(pk=current_company)

    perm_list = item.getItemInstPermList(request.user)

    '''
    if 'add_adv_banner' not in perm_list:
        return HttpResponseRedirect(reverse('denied'))
    '''
    ads = AdvertisementItem.objects.filter(c2p__parent=current_company).order_by('-create_date')

    paginator = Paginator(ads, 10)

    advOnPage = paginator.page(page)

    advIDs = [adv.pk for adv in advOnPage.object_list]

    advAttrValues = Item.getItemsAttributesValues(('COST', 'END_EVENT_DATE', 'START_EVENT_DATE'), advIDs)

    adv = {}

    for advObj in advOnPage.object_list:

        if advObj.pk not in advAttrValues or not isinstance(advAttrValues[advObj.pk], dict):
            advAttr = {}
            advAttrValues[advObj.pk] = {}
        else:
            advAttr = advAttrValues[advObj.pk]

        end_event_date = parse(advAttr.get('END_EVENT_DATE', [None])[0]).strftime("%Y-%m-%d")
        start_event_date = parse(advAttr.get('START_EVENT_DATE', [None])[0]).strftime("%Y-%m-%d")

        if now() >= advObj.end_date:
            active = 2
        else:

            if not end_event_date:
                active = 0
            else:
                active = 1 if (end_event_date == advObj.end_date.strftime("%Y-%m-%d")) else 0



        if getattr(advObj, 'adv_top', None):
            type = _('Top')
        else:
            type = _('Banner')

        summary = '{0:.2f}'.format(float(advAttr.get('COST', [0])[0]))

        adv[advObj.pk] = {
            'type': type,
            'status': active,
            'end_date': end_event_date,
            'start_date': start_event_date,
            'total': '{0:,}'.format(float(summary))
        }



    templatePatams = {
        'adv': adv,
        'page': page,
        'paginator_range': func.getPaginatorRange(advOnPage),
        'url_paginator': "Adv:basket_paginator",
    }

    return render_to_response("Adv/basket.html", templatePatams, context_instance=RequestContext(request))