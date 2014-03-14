__author__ = 'user'
from django.shortcuts import HttpResponse, render_to_response, get_object_or_404, HttpResponseRedirect
from appl.models import *
from django.template import RequestContext, loader
from django.utils.translation import ugettext as _
from tppcenter.forms import ItemForm
from django.core.urlresolvers import reverse
from django.conf import settings
from core.tasks import addTopAttr

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

    current_organization = request.session.get('current_company', False)

    if current_organization is False:
        return render_to_response("permissionDen.html")

    org = Organization.objects.get(pk=current_organization)
    #org = Organization.objects.get(pk=114)

    perm_list = org.getItemInstPermList(request.user)

    if 'add_tops' not in perm_list:
         return render_to_response("permissionDenied.html")


    itemName = object.getAttributeValues('NAME')[0]

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
                addTopAttr(request.POST, object, user, settings.SITE_ID, ids, org)
            except Exception as e:
                form.errors.update({"ERROR": _("Error occurred while trying to proceed your request")})

            if form.is_valid():
                return HttpResponseRedirect(reverse('news:main'))



    enable = {
        'branch': {'placeholder': _('Select branch'), 'init': len(filter.get('branch', []))},
        'country': {'placeholder': _('Select country'), 'init': len(filter.get('country', []))},
        'tpp': {'placeholder': _('Select organization'), 'init': len(filter.get('tpp', []))}
    }

    current_section = _('Banners')

    templateParams = {
        'current_section': current_section,
        'enable': enable,
        'form': form,
        'stDate': stDate,
        'edDate': edDate,
        'filterAttr': filterAttr,
        'filters': filter,
        'itemName': itemName
    }

    return render_to_response('AdvTop/addForm.html', templateParams, context_instance=RequestContext(request))
