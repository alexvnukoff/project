__author__ = 'user'
from appl.models import AdvBannerType, AdvBanner, Cabinet
from core.models import Item
from django.shortcuts import HttpResponse, render_to_response, get_object_or_404
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

    btype = get_object_or_404(AdvBannerType, pk=bannerType)

    enable = {}

    if btype.enableBranch:
        enable['branch'] = _('Select branch')

    if btype.enableCountry:
        enable['country'] = _('Select country')

    if btype.enableTpp:
        enable['tpp'] = _('Select organization')


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
        'enable': enable
    }

    return render_to_response("AdvBanner/detail.html", templateParams, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def advJsonFilter(request):
    import json

    filter = request.GET.get('type', None)
    q = request.GET.get('q', '')
    page = request.GET.get('page', None)


    if request.is_ajax() and type and page and (len(q) == 0 or len(q) > 2):
        from haystack.query import SearchQuerySet
        from django.core.paginator import Paginator

        model = None


        if filter == 'tpp':
            model = Tpp
        elif filter == "companies":
            model = Company
        elif filter == "category":
            model = Category
        elif filter == "branch":
            model = Branch
        elif filter == 'country':
            model = Country

        if model:

            if not q:
                sqs = SearchQuerySet().models(model).order_by('title').order_by('title')
            else:
                sqs = SearchQuerySet().models(model).filter(title_auto=q)

            paginator = Paginator(sqs, 10)

            try:
                onPage = paginator.page(page)
            except Exception:
                onPage = paginator.page(1)

            total = paginator.count

            obj_list = [item.id for item in onPage.object_list]

            itemsAttr = Item.getItemsAttributesValues('COST', obj_list)
            items = []

            for item in onPage.object_list:

                if not isinstance(itemsAttr[item.id], dict) :
                    itemsAttr[item.id] = {}

                resultDict = {
                    'title': item.title_auto,
                    'id': item.id,
                    'cost': itemsAttr[item.id].get('COST', [0])[0],
                }

                items.append(resultDict)

            return HttpResponse(json.dumps({'content': items, 'total': total}))

    return HttpResponse(json.dumps({'content': [], 'total': 0}))