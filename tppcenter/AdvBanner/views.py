import json
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView

from appl import func
from appl.models import Tpp, AdvBannerType, Branch, Country, AdvOrder
from b24online.models import BannerBlock, Banner, AdvertisementPrices
from core.models import Item

# from core.tasks import addBannerAttr
from django.core.urlresolvers import reverse
from django.core.files.images import ImageFile
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import HttpResponse, render_to_response, get_object_or_404, HttpResponseRedirect
from django.utils.translation import ugettext as _
from tppcenter.AdvBanner.forms import BannerForm
from tppcenter.forms import ItemForm
from dateutil.parser import parse
import datetime


class BannerBlockList(ListView):
    template_name = 'AdvBanner/index.html'
    context_object_name = 'blocks'
    ordering = 'block_type, name'

    def get_queryset(self):
        return BannerBlock.objects.filter(block_type__in=['b2c', 'b2b'])

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        sites = {}

        for block in context_data['blocks']:
            site_name = block.get_block_type_display()

            if site_name not in sites:
                sites[site_name] = []

            sites[site_name].append(block)

            context_data['sites'] = sites

        return context_data


class CreateBanner(CreateView):
    model = Banner
    form_class = BannerForm
    template_name = 'AdvBanner/addForm.html'
    success_url = None

    # TODO: check permission
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.block_id = kwargs.pop('block_id')
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        form.instance.dates = (form.cleaned_data['start_date'], form.cleaned_data['end_date'])

        


    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['banner_block'] = BannerBlock.objects.get(pk=self.block_id, block_type__in=['b2c', 'b2b'])
        cleaned_data = getattr(context_data['form'], 'cleaned_data', None)

        if cleaned_data:
            for valid_filter in ['branches', 'country', 'chamber']:
                obj_list = cleaned_data.get(valid_filter, None)

                if obj_list:
                    model_type = ContentType.objects.get_for_model(obj_list[0])
                    prices = AdvertisementPrices.objects.filter(content_type__pk=model_type.pk,
                                                                object_id__in=obj_list,
                                                                advertisement_type='banner')
                    price_dict = dict((p.object_id, p.price) for p in prices)
                    context_data[valid_filter] =[]

                    for item in obj_list:
                        cost = price_dict.get(item.pk, 0)

                        context_data[valid_filter].append({
                            'name': item.name,
                            'id': item.pk,
                            'cost': cost,
                        })

        return context_data


@login_required
def adv_json_filter(request):
    """
        Getting filters for advertisement
    """
    filter_model = request.GET.get('type', None)
    q = request.GET.get('q', '').strip()

    try:
        page = int(request.GET.get('page', None))
    except ValueError:
        return HttpResponse(json.dumps({'content': [], 'total': 0}))

    if filter_model and (len(q) >= 3 or len(q) == 0):
        obj_list, total = func.autocomplete_filter(filter_model, q, page)

        if total > 0:
            model_type = ContentType.objects.get_for_model(obj_list[0])
            prices = AdvertisementPrices.objects.filter(content_type__pk=model_type.pk,
                                                        object_id__in=obj_list,
                                                        advertisement_type='banner')
            price_dict = dict((p.object_id, p.price) for p in prices)
            items = []

            for item in obj_list:
                cost = price_dict.get(item.pk, 0)

                result_dict = {
                    'title': item.name,
                    'id': item.pk,
                    'cost': cost,
                }

                items.append(result_dict)

            return HttpResponse(json.dumps({'content': items, 'total': total}))

    return HttpResponse(json.dumps({'content': [], 'total': 0}))


@login_required
def addBanner(request, bannerType):
    '''
        View for a form of adding new banners
    '''
    '''
    current_company = request.session.get('current_company', False)

    if not request.session.get('current_company', False):
         return func.emptyCompany()

    item = Organization.objects.get(pk=current_company)

    perm_list = item.getItemInstPermList(request.user)

    if 'add_adv_banner' not in perm_list:
        return HttpResponseRedirect(reverse('denied'))
    '''

    btype = get_object_or_404(AdvBannerType, pk=bannerType)
    properties = btype.getAttributeValues('HEIGHT', 'WIDTH', 'FACTOR')

    if not isinstance(properties, dict):
        properties = {}

    bannerHeight = int(properties.get('HEIGHT', [0])[0])
    bannerWidth = int(properties.get('WIDTH', [0])[0])
    factor = float(properties.get('FACTOR', [1])[0])

    form = None
    stDate = ''
    edDate = ''
    filterAttr = {}
    filter = {'branch': [], 'country': [], 'tpp': []}

    if request.POST:
        user = request.user

        values = {}
        values['NAME'] = request.POST.get('NAME', "")
        values['SITE_NAME'] = request.POST.get('SITE_NAME', "")
        values['IMAGE'] = request.FILES.get('IMAGE', "")

        values['START_EVENT_DATE'] = request.POST.get('st_date', '')
        values['END_EVENT_DATE'] = request.POST.get('ed_date', '')
        values['COST'] = 0

        stDate = values['START_EVENT_DATE']
        edDate = values['END_EVENT_DATE']

        # allowed filters
        filterList = ['tpp', 'country', 'branch']
        ids = []

        for name in filterList:  # Get filters form request context

            for pk in request.POST.getlist('filter[' + name + '][]', []):
                try:
                    ids.append(int(pk))
                except ValueError:
                    continue


        # Get filter objects
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

        # Get name and cost of each filter for form initial values (if error occur on previous submit)
        filterAttr = Item.getItemsAttributesValues(('COST', 'NAME'), ids)

        for id in ids:
            if not isinstance(filterAttr[id], dict):
                filterAttr[id] = {}

            filterAttr[id]['NAME'] = filterAttr[id].get('NAME', [''])[0]
            filterAttr[id]['COST'] = filterAttr[id].get('COST', [0])[0]

        form = ItemForm('AdvBanner', values=values)
        form.clean()

        if form.is_valid():

            if len(ids) == 0:
                form.errors.update({"FILTER": _("You must choose one filter al least")})

            if form.is_valid():

                # 50 KB file
                if form.is_valid() and (not values['IMAGE'] or values['IMAGE'].size > 50 * 1024):
                    form.errors.update({"IMAGE": _("The image size cannot exceed 50 KB")})

                if form.is_valid():
                    im = ImageFile(values['IMAGE'])

                    if im.height != bannerHeight or im.width != bannerWidth:
                        form.errors.update({"IMAGE": _("Image dimension should not exceed")})

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
                current_company = request.session.get('current_company', False)
                # order = addBannerAttr(request.POST, request.FILES, user, settings.SITE_ID, ids, btype, current_company,
                #                       factor)
            except Exception as e:
                form.errors.update({"ERROR": _("Error occurred while trying to proceed your request")})

            if form.is_valid():
                return HttpResponseRedirect(reverse('adv_banners:resultOrder', args=(order,)))

    enable = {}

    if btype.enableBranch:
        enable['branch'] = {'placeholder': _('Select branch'), 'init': len(filter.get('branch', []))}

    if btype.enableCountry:
        enable['country'] = {'placeholder': _('Select country'), 'init': len(filter.get('country', []))}

    if btype.enableTpp:
        enable['tpp'] = {'placeholder': _('Select organization'), 'init': len(filter.get('tpp', []))}

    current_section = _('Banners')

    templateParams = {
        'current_section': current_section,
        'enable': enable,
        'form': form,
        'stDate': stDate,
        'edDate': edDate,
        'filterAttr': filterAttr,
        'filters': filter,
        'factor': factor
    }

    return render_to_response('AdvBanner/addForm.html', templateParams, context_instance=RequestContext(request))


@login_required
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

    ordWithValues = order.getAttributeValues('ORDER_HISTORY', 'ORDER_DAYS', 'COST', 'START_EVENT_DATE',
                                             'END_EVENT_DATE', 'IMAGE')

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
            attrValues.get('NAME', [""])[0]: cost
        })

    startDate = parse(ordWithValues.get('START_EVENT_DATE', [""])[0]).strftime('%d/%m/%Y')
    endDate = parse(ordWithValues.get('END_EVENT_DATE', [""])[0]).strftime('%d/%m/%Y')

    current_section = _('Banners')

    templateParams = {
        'current_section': current_section,
        'nameCost': nameCostDict,
        'totalCost': ordWithValues.get('COST', [0])[0],
        'startDate': startDate,
        'endDate': endDate,
        'totalDays': ordWithValues.get('ORDER_DAYS', [0])[0],
        'IMAGE': ordWithValues.get('IMAGE', [''])[0],
        'order': orderID
    }

    return render_to_response('AdvBanner/order.html', templateParams, context_instance=RequestContext(request))
