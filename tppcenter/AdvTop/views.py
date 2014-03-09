__author__ = 'user'
from appl.models import AdvBannerType, AdvBanner, Cabinet
from core.models import Item
from django.shortcuts import HttpResponse, render_to_response, get_object_or_404, HttpResponseRedirect
from appl.models import *
from django.db.models import ObjectDoesNotExist, Count
from appl import func
from django.template import RequestContext, loader
from django.utils.translation import ugettext as _
from tppcenter.forms import ItemForm
from django.core.urlresolvers import reverse
from django.conf import settings
from core.tasks import addTopAttr
from django.core.files.images import ImageFile
from django.db import transaction
from copy import copy

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


@login_required(login_url='/login/')
def addTop(request, item):

    object = get_object_or_404(Item, pk=item)

    form = None
    stDate = ''
    edDate = ''
    filterAttr = {}
    filter = {'branch': [], 'country': [], 'tpp': []}


    if request.POST:
        user = request.user

        stDate = request.POST.get('st_date', '')
        edDate = request.POST.get('ed_date', '')

        filterList = ['tpp', 'country', 'branch']
        ids = []

        for name in filterList:

            for pk in request.POST.getlist('filter[' + name + '][]', []):
                try:
                    ids.append(int(pk))
                except ValueError:
                    continue

        tpps = Tpp.objects.filter(pk__in=ids)
        countries = Country.objects.filter(pk__in=ids)
        branches = Branch.objects.filter(pk__in=ids)

        ids = []
        filter = {}

        if tpps.exists():
            filter['tpp'] = tpps.values_list('pk', flat=True)
            ids += filter['tpp']

        if countries.exists():
            filter['country'] = countries.values_list('pk', flat=True)
            ids += filter['country']

        if branches.exists():
            filter['branch'] = branches.values_list('pk', flat=True)
            ids += filter['branch']

        filterAttr = Item.getItemsAttributesValues(('COST', 'NAME'), ids)

        for id in ids:
            if not isinstance(filterAttr[id], dict):
                filterAttr[id] = {}

            filterAttr[id]['NAME'] = filterAttr[id].get('NAME', [''])[0]
            filterAttr[id]['COST'] = filterAttr[id].get('COST', [0])[0]

        form = ItemForm('AdvTop', values={})
        form.clean()

        if form.is_valid():

            if len(ids) == 0:
                form.errors.update({"FILTER": _("You must choose one filter al least")})

            if form.is_valid():

                try:
                    startDate = datetime.datetime.strptime(stDate, "%m/%d/%Y")
                    endDate = datetime.datetime.strptime(edDate, "%m/%d/%Y")
                except ValueError:
                    form.errors.update({"DATE": _("You should choose a valid date range")})

                if form.is_valid():
                    if not startDate or not endDate:
                        form.errors.update({"DATE": _("You should choose a date range")})

                    delta = endDate - startDate

                    if delta.days <= 0:
                        form.errors.update({"DATE": _("You should choose a valid date range")})

        if form.is_valid():
            try:
                addTopAttr(request.POST, object, user, settings.SITE_ID, ids)
            except Exception as e:
                form.errors.update({"ERROR": _("Error occurred while trying to proceed your request")})

            if form.is_valid():
                return HttpResponseRedirect(reverse('news:main'))



    enable = {}


    enable['branch'] = _('Select branch')
    enable['country'] = _('Select country')
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
        'enable': enable,
        'form': form,
        'stDate': stDate,
        'edDate': edDate,
        'filterAttr': filterAttr,
        'filters': filter
    }

    return render_to_response('AdvTop/addForm.html', templateParams, context_instance=RequestContext(request))