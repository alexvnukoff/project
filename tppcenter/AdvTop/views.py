import json
from dateutil.parser import parse
from django.contrib.sites.models import Site
from appl.models import Organization, Branch, Tpp, Country, AdvOrder
from core.models import Item
from core.tasks import addTopAttr
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import HttpResponse, render_to_response, get_object_or_404, HttpResponseRedirect
from django.utils.translation import ugettext as _
from tppcenter.forms import ItemForm
#from paypal.standard.forms import PayPalPaymentsForm
import datetime

@login_required(login_url='/login/')
def advJsonFilter(request):
    '''
        Getting filters for advertisement
    '''

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
        elif filter == "branch":
            model = Branch
        elif filter == 'country':
            model = Country

        if model:

            if not q:
                sqs = SearchQuerySet().models(model).order_by('title')
            else:
                sqs = SearchQuerySet().models(model).autocomplete(title_auto=q).order_by('title_sort')

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
    '''
        View for a form of adding new context adv
    '''

    object = get_object_or_404(Item, pk=item)
    factor = float(object.contentType.top.getAttributeValues('COST')[0])

    current_organization = request.session.get('current_company', False)

    if current_organization is False:
        return HttpResponseRedirect(reverse('denied'))

    org = Organization.objects.get(pk=current_organization)
    #org = Organization.objects.get(pk=114)
    '''
    perm_list = org.getItemInstPermList(request.user)

    if 'add_advtop' not in perm_list:
         return HttpResponseRedirect(reverse('denied'))
    '''

    itemName = object.getAttributeValues('NAME')[0]

    form = None
    stDate = ''
    edDate = ''
    filterAttr = {}
    filter = {'branch': [], 'country': [], 'tpp': []}


    if request.POST:
        user = request.user

        values = {}

        values['START_EVENT_DATE'] = request.POST.get('st_date', '')
        values['END_EVENT_DATE'] = request.POST.get('ed_date', '')
        values['COST'] = 0

        stDate = values['START_EVENT_DATE']
        edDate = values['END_EVENT_DATE']

        #Allowed filters
        filterList = ['tpp', 'country', 'branch']
        ids = []

        for name in filterList: #Get filters from the request context

            for pk in request.POST.getlist('filter[' + name + '][]', []):
                try:
                    ids.append(int(pk))
                except ValueError:
                    continue


        #Get filter objects
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

        #Get name and cost of each filter for form initial values (if error occur on previous submit)
        filterAttr = Item.getItemsAttributesValues(('COST', 'NAME'), ids)

        for itemID in ids:
            if not isinstance(filterAttr[itemID], dict):
                filterAttr[itemID] = {}

            filterAttr[itemID]['NAME'] = filterAttr[itemID].get('NAME', [''])[0]
            filterAttr[itemID]['COST'] = filterAttr[itemID].get('COST', [0])[0]

        form = ItemForm('AdvTop', values=values)
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
                    startDate = None
                    endDate = None

                if form.is_valid():
                    if not startDate or not endDate:
                        form.errors.update({"DATE": _("You should choose a date range")})

                    delta = endDate - startDate

                    if delta.days <= 0:
                        form.errors.update({"DATE": _("You should choose a valid date range")})

        order = None

        if form.is_valid():
            try:
                order = addTopAttr(request.POST, object, user, settings.SITE_ID, ids, org, factor)
            except Exception as e:
                form.errors.update({"ERROR": _("Error occurred while trying to proceed your request")})

            if form.is_valid():
                return HttpResponseRedirect(reverse('adv_top:resultOrder', args=(order, )))



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
        'itemName': itemName,
        'factor': factor
    }

    return render_to_response('AdvTop/addForm.html', templateParams, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def resultOrder(request, orderID):


    current_company = request.session.get('current_company', False)
    '''
    if not request.session.get('current_company', False):
         return func.emptyCompany()

    item = Organization.objects.get(pk=current_company)

    perm_list = item.getItemInstPermList(request.user)

    if 'add_adv_banner' not in perm_list:
        return HttpResponseRedirect(reverse('denied'))
    '''

    order = get_object_or_404(AdvOrder, pk=orderID, c2p__parent=current_company)

    ordWithValues = order.getAttributeValues('ORDER_HISTORY', 'ORDER_DAYS', 'COST', 'START_EVENT_DATE', 'END_EVENT_DATE', 'IMAGE')

    ordJson = ordWithValues.get('ORDER_HISTORY', [""])[0]

    orderHistory = json.loads(ordJson)

    ids = orderHistory.get('ids', [])

    placeNames = Item.getItemsAttributesValues('NAME', ids)

    nameCostDict = {}

    for pid, cost in orderHistory.get('costs', {}).items():



        if int(pid) in placeNames:
            attrValues = placeNames[int(pid)]
        else:
            attrValues = {}

        if isinstance(attrValues, int):
            attrValues = {}

        nameCostDict.update({
            attrValues.get('NAME', [""])[0] : cost
        })

    startDate = parse(ordWithValues.get('START_EVENT_DATE', [""])[0]).strftime('%d/%m/%Y')
    endDate = parse(ordWithValues.get('END_EVENT_DATE', [""])[0]).strftime('%d/%m/%Y')

    current_section = _('Tops')
    '''
    domain = Site.objects.get(pk=1).domain
    cost = '{0:.2f}'.format(ordWithValues.get('COST', [0])[0])

        # What you want the button to do.
    paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": cost,
        "item_name": _('Advertisement'),
        "invoice": orderID,
        "notify_url": "http://www." + domain + '/' + reverse('paypal-ipn'),
        "return_url": "http://www." + domain + '/',
        "cancel_return": "http://www." + domain + '/',

    }

    # Create the instance.
    form = PayPalPaymentsForm(initial=paypal_dict)
    '''

    templateParams = {
        'current_section': current_section,
        'nameCost': nameCostDict,
        'totalCost': cost,
        'startDate': startDate,
        'endDate': endDate,
        'totalDays': ordWithValues.get('ORDER_DAYS', [0])[0],
        'order': orderID
        #"form": form
    }

    return render_to_response('AdvTop/order.html', templateParams, context_instance=RequestContext(request))
