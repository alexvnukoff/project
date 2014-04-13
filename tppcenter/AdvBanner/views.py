from appl.models import Tpp, Company, Category, AdvBannerType, Branch, Country
from core.models import Item
from core.tasks import addBannerAttr
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.files.images import ImageFile
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import HttpResponse, render_to_response, get_object_or_404, HttpResponseRedirect
from django.utils.translation import ugettext as _
from tppcenter.forms import ItemForm
import datetime

@login_required(login_url='/login/')
def gatPositions(request):
    '''
        Show possible advertisement position as a first page and show them by site
    '''

    bannerType = AdvBannerType.objects.all().values('pk', 'sites__name')

    bannerType_ids = [btype['pk'] for btype in bannerType]
    bannerNames = Item.getItemsAttributesValues('NAME', bannerType_ids)
    sites = {}

    for btype in bannerType:

        if btype['sites__name'] not in sites:
            sites[btype['sites__name']] = {}

        if btype['pk'] in bannerNames:
            sites[btype['sites__name']][btype['pk']] = bannerNames[btype['pk']]

    current_section = _('Banners')


    templateParams = {
        'sites': sites,
        'current_section': current_section,
    }

    return render_to_response("AdvBanner/index.html", templateParams, context_instance=RequestContext(request))

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
                sqs = SearchQuerySet().models(model).order_by('title_sort')
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
def addBanner(request, bannerType):
    '''
        View for a form of adding new banners
    '''

    btype = get_object_or_404(AdvBannerType, pk=bannerType)

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

        stDate = request.POST.get('st_date', '')
        edDate = request.POST.get('ed_date', '')

        #allowed filters
        filterList = ['tpp', 'country', 'branch']
        ids = []

        for name in filterList: # Get filters form request context

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

        #Get name and cost of each filter for form initial values (if error occur on previous submit)
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

                #50 KB file
                if form.is_valid() and (not values['IMAGE'] or values['IMAGE'].size > 50 * 1024):
                    form.errors.update({"IMAGE": _("The image size cannot exceed 50 KB")})

                if form.is_valid():
                    im = ImageFile(values['IMAGE'])

                    if im.height > 100 and im.width > 200:
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

        if form.is_valid():
            try:
                current_company = request.session.get('current_company', False)
                addBannerAttr(request.POST, request.FILES, user, settings.SITE_ID, ids, btype, current_company)
            except Exception as e:
                form.errors.update({"ERROR": _("Error occurred while trying to proceed your request")})

            if form.is_valid():
                return HttpResponseRedirect(reverse('news:main'))



    enable = {}

    if btype.enableBranch:
        enable['branch'] = _('Select branch')

    if btype.enableCountry:
        enable['country'] = _('Select country')

    if btype.enableTpp:
        enable['tpp'] = _('Select organization')

    current_section = _('Banners')

    templateParams = {
        'current_section': current_section,
        'enable': enable,
        'form': form,
        'stDate': stDate,
        'edDate': edDate,
        'filterAttr': filterAttr,
        'filters': filter
    }

    return render_to_response('AdvBanner/addForm.html', templateParams, context_instance=RequestContext(request))