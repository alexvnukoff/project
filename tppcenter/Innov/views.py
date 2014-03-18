from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response, get_object_or_404
from appl.models import *
from django.http import HttpResponseRedirect, HttpResponse
from core.models import Item, Dictionary
from appl import func
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import modelformset_factory
from tppcenter.forms import ItemForm, BasePhotoGallery, BasePages
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from core.tasks import addNewProject
from django.conf import settings
from haystack.query import SQ, SearchQuerySet
import json
from django.core.cache import cache


def get_innov_list(request, page=1, item_id=None, my=None, slug=None):
   # if slug and  not Value.objects.filter(item=item_id, attr__title='SLUG', title=slug).exists():
    #     slug = Value.objects.get(item=item_id, attr__title='SLUG').title
     #    return HttpResponseRedirect(reverse('innov:detail',  args=[slug]))

    current_company = request.session.get('current_company', False)
    description = ''
    if current_company:
        current_company = Organization.objects.get(pk=current_company).getAttributeValues("NAME")

    cabinetValues = func.getB2BcabinetValues(request)

    styles = [
        settings.STATIC_URL + 'tppcenter/css/news.css',
        settings.STATIC_URL + 'tppcenter/css/company.css'
    ]

    scripts = []

    if item_id is None:
        try:
            newsPage = _innovContent(request, page, my)
        except ObjectDoesNotExist:
            newsPage = func.emptyCompany()
    else:
       result  = _innovDetailContent(request, item_id)
       newsPage = result[0]
       description = result[1]

    if not request.is_ajax():

        current_section = _("Innovation Project")

        templateParams = {
            'newsPage': newsPage,
            'current_section': current_section,
            'scripts': scripts,
            'styles': styles,
            'search': request.GET.get('q', ''),
            'current_company': current_company,
            'addNew': reverse('innov:add'),
            'cabinetValues': cabinetValues,
            'item_id': item_id,
            'description': description
        }

        return render_to_response("Innov/index.html", templateParams, context_instance=RequestContext(request))

    else:

        serialize = {
            'styles': styles,
            'scripts': scripts,
            'content': newsPage
        }

        return HttpResponse(json.dumps(serialize))



def _innovContent(request, page=1, my=None):
    cached = False
    cache_name = "inov_list_result_page_%s" % page
    query = request.GET.urlencode()
    if query.find('filter') == -1 and not my and not request.user.is_authenticated():
        cached = cache.get(cache_name)
    if not cached:


        if not my:
            filters, searchFilter = func.filterLive(request)

            sqs = func.getActiveSQS().models(InnovationProject)

            if len(searchFilter) > 0:
                sqs = sqs.filter(**searchFilter)

            q = request.GET.get('q', '')

            if q != '':
                sqs = sqs.filter(SQ(title=q) | SQ(text=q))

            sortFields = {
                'date': 'id',
                'name': 'title'
            }

            order = []

            sortField1 = request.GET.get('sortField1', 'date')
            sortField2 = request.GET.get('sortField2', None)
            order1 = request.GET.get('order1', 'desc')
            order2 = request.GET.get('order2', None)

            if sortField1 and sortField1 in sortFields:
                if order1 == 'desc':
                    order.append('-' + sortFields[sortField1])
                else:
                    order.append(sortFields[sortField1])
            else:
                order.append('-id')

            if sortField2 and sortField2 in sortFields:
                if order2 == 'desc':
                    order.append('-' + sortFields[sortField2])
                else:
                    order.append(sortFields[sortField2])


            innov_projects = sqs.order_by(*order)
            url_paginator = "innov:paginator"

            params = {
                'filters': filters,
                'sortField1': sortField1,
                'sortField2': sortField2,
                'order1': order1,
                'order2': order2
            }

        else:
            current_organization = request.session.get('current_company', False)

            if current_organization:
                innov_projects = SearchQuerySet().models(InnovationProject)
                innov_projects = innov_projects.filter(SQ(tpp=current_organization) | SQ(company=current_organization))

                url_paginator = "innov:my_main_paginator"
                params = {}

            else: #TODO Jenya do block try
                raise ObjectDoesNotExist('you need check company')

        result = func.setPaginationForSearchWithValues(innov_projects, *('NAME', 'SLUG'), page_num=7, page=page)

        innovList = result[0]
        innov_ids = [id for id in innovList.keys()]

        cabinets = Cabinet.objects.filter(p2c__child__in=innov_ids).values('p2c__child', 'pk')

        cabinets_ids = [cabinet['pk'] for cabinet in cabinets]
        countries = Country.objects.filter(p2c__child__in=cabinets_ids).values('p2c__child', 'pk')

        countries_id = [country['pk'] for country in countries]
        countriesList = Item.getItemsAttributesValues(("NAME", 'FLAG'), countries_id)

        country_dict = {}

        for country in countries:
            if country['pk']:
               country_dict[country['p2c__child']] = country['pk']

        cabinetList = Item.getItemsAttributesValues(("USER_FIRST_NAME", 'USER_LAST_NAME'), cabinets_ids)

        cabinets_dict = {}

        for cabinet in cabinets:
            cabinets_dict[cabinet['p2c__child']] = {
                'CABINET_NAME': cabinetList[cabinet['pk']].get('USER_FIRST_NAME', 0) if cabinetList.get(cabinet['pk'], 0) else [0],
                'CABINET_LAST_NAME': cabinetList[cabinet['pk']].get('USER_LAST_NAME', 0) if cabinetList.get(cabinet['pk'], 0) else [0],
                'CABINET_ID': cabinet['pk'],
                'CABINET_COUNTRY_NAME': countriesList[country_dict[cabinet['pk']]].get('NAME', [0]) if country_dict.get(cabinet['pk'], False) else [0],
                'CABINET_COUNTRY_FLAG': countriesList[country_dict[cabinet['pk']]].get('FLAG', [0]) if country_dict.get(cabinet['pk'], False) else [0],
                'CABINET_COUNTRY_ID': country_dict.get(cabinet['pk'], "")
            }

        branches = Branch.objects.filter(p2c__child__in=innov_ids).values('p2c__child', 'pk')
        branches_ids = [branch['pk'] for branch in branches]
        branchesList = Item.getItemsAttributesValues(("NAME"), branches_ids)

        branches_dict = {}

        for branch in branches:
            branches_dict[branch['p2c__child']] = branch['pk']

        func.addDictinoryWithCountryAndOrganization(innov_ids, innovList)

        for id, innov in innovList.items():

            toUpdate = {
                'BRANCH_NAME': branchesList[branches_dict[id]].get('NAME', 0) if branches_dict.get(id, 0) else [0],
                'BRANCH_ID': branches_dict.get(id, 0),
            }

            innov.update(toUpdate)

            if cabinets_dict.get(id, 0):
               innov.update(cabinets_dict.get(id, 0))

        page = result[1]
        paginator_range = func.getPaginatorRange(page)

        template = loader.get_template('Innov/contentPage.html')

        templateParams = {
            'innovList': innovList,
            'page': page,
            'paginator_range': paginator_range,
            'url_paginator': url_paginator,

        }

        templateParams.update(params)

        context = RequestContext(request, templateParams)
        rendered = template.render(context)
        if not my and query.find('filter') == -1 and not request.user.is_authenticated():
           cache.set(cache_name, rendered)

    else:
        rendered = cache.get(cache_name)
    return rendered



def _innovDetailContent(request, item_id):

    innov = get_object_or_404(InnovationProject, pk=item_id)

    attr = ('NAME', 'PRODUCT_NAME', 'COST', 'REALESE_DATE', 'BUSINESS_PLAN', 'CURRENCY', 'DOCUMENT_1', 'DETAIL_TEXT')

    innovValues = innov.getAttributeValues(*attr)
    description = innovValues.get('DETAIL_TEXT', False)[0] if innovValues.get('DETAIL_TEXT', False) else ""
    description = func.cleanFromHtml(description)

    photos = Gallery.objects.filter(c2p__parent=item_id)

    additionalPages = AdditionalPages.objects.filter(c2p__parent=item_id)

    try:
        branch = Branch.objects.get(p2c__child=item_id)
        branchValues = branch.getAttributeValues('NAME')
        innovValues.update({'BRANCH_NAME': branchValues, 'BRANCH_ID': branch.id})
    except ObjectDoesNotExist:
        innovValues.update({'BRANCH_NAME': [0], 'BRANCH_ID': 0})


    func.addToItemDictinoryWithCountryAndOrganization(innov.id, innovValues)

    cabinet = Cabinet.objects.filter(p2c__child=item_id)

    if cabinet.exists():
        cabinetList = cabinet[0].getAttributeValues("USER_FIRST_NAME", 'USER_LAST_NAME')
        country = Country.objects.filter(p2c__child=cabinet)

        if country.exists():
            countriesList = country[0].getAttributeValues("NAME", 'FLAG')
            countryUpdate = {
                'CABINET_COUNTRY_ID': country[0].pk,
                'CABINET_COUNTRY_FLAG': countriesList.get('FLAG', [0]),
                'CABINET_COUNTRY_NAME':  countriesList.get('NAME', [0])
            }
        else:
            countryUpdate = {}

        cabinetUpdate = {
            'CABINET_ID': cabinet[0].pk,
            'CABINET_FIRST_NAME': cabinetList.get('USER_FIRST_NAME', [0]),
            'CABINET_LAST_NAME': cabinetList.get('USER_LAST_NAME', [0])
        }

    else:
        cabinetUpdate = {}
        countryUpdate = {}


    template = loader.get_template('Innov/detailContent.html')

    templateParams = {
        'innovValues': innovValues,
        'photos': photos,
        'additionalPages': additionalPages,
        'countryUpdate': countryUpdate,
        'cabinetUpdate': cabinetUpdate
    }

    context = RequestContext(request, templateParams)

    return template.render(context), description

@login_required(login_url='/login/')
def innovForm(request, action, item_id=None):
    cabinetValues = func.getB2BcabinetValues(request)

    current_company = request.session.get('current_company', False)

    if current_company:
        current_company = Organization.objects.get(pk=current_company).getAttributeValues("NAME")

    current_section = _("Innovation Project")

    if action == 'add':
        newsPage = addProject(request)
    else:
        newsPage = updateProject(request, item_id)

    if isinstance(newsPage, HttpResponseRedirect) or isinstance(newsPage, HttpResponse):
        return newsPage

    templateParams = {
        'newsPage': newsPage,
        'current_company':current_company,
        'current_section': current_section,
        'cabinetValues': cabinetValues
    }

    return render_to_response('Innov/index.html', templateParams, context_instance=RequestContext(request))

def addProject(request):
    current_company = request.session.get('current_company', False)

    if not request.session.get('current_company', False):
         return func.emptyCompany()

    item = Organization.objects.get(pk=current_company)

    perm_list = item.getItemInstPermList(request.user)



    if 'add_innovationproject' not in perm_list:
         return func.permissionDenied()


    form = None

    branches = Branch.objects.all()
    branches_ids = [branch.id for branch in branches]
    branches = Item.getItemsAttributesValues(("NAME",), branches_ids)

    currency = Dictionary.objects.get(title='CURRENCY')
    currency_slots = currency.getSlotsList()

    if request.POST:

        user = request.user

        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=5, fields=("photo",))
        gallery = Photo(request.POST, request.FILES)

        Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
        pages = Page(request.POST, request.FILES, prefix="pages")

        values = _getValues(request)

        branch = request.POST.get('BRANCH', "")

        form = ItemForm('InnovationProject', values=values)
        form.clean()

        if gallery.is_valid() and form.is_valid() and pages.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addNewProject.delay(request.POST, request.FILES, user, settings.SITE_ID, branch=branch, current_company=current_company, lang_code=settings.LANGUAGE_CODE)
            return HttpResponseRedirect(reverse('innov:main'))


    template = loader.get_template('Innov/addForm.html')
    context = RequestContext(request, {'form': form, 'branches': branches, 'currency_slots': currency_slots})
    newsPage = template.render(context)


    return newsPage



def updateProject(request, item_id):
    try:
        item = Organization.objects.get(p2c__child_id=item_id)
    except ObjectDoesNotExist:
        item = Cabinet.objects.get(p2c__child_id=item_id)

    perm_list = item.getItemInstPermList(request.user)
    if 'change_innovationproject' not in perm_list:
        return func.permissionDenied()

    branches = Branch.objects.all()
    branches_ids = [branch.id for branch in branches]
    branches = Item.getItemsAttributesValues(("NAME",), branches_ids)
    try:
        currentBranch = Branch.objects.get(p2c__child=item_id)
    except Exception:
        currentBranch = ""

    Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
    pages = Page(request.POST, request.FILES, prefix="pages", parent_id=item_id)
    pages = pages.queryset

    Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=5, fields=("photo",))
    gallery = Photo(parent_id=item_id)
    photos = ""

    if gallery.queryset:
        photos = [{'photo': image.photo, 'pk': image.pk} for image in gallery.queryset]

    currency = Dictionary.objects.get(title='CURRENCY')
    currency_slots = currency.getSlotsList()

    form = ItemForm('InnovationProject', id=item_id)

    if request.POST:


        user = request.user
        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=5, fields=("photo",))
        gallery = Photo(request.POST, request.FILES)

        Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
        pages = Page(request.POST, request.FILES, prefix="pages")

        values = _getValues(request)

        branch = request.POST.get('BRANCH', "")

        form = ItemForm('InnovationProject', values=values, id=item_id)
        form.clean()

        if gallery.is_valid() and form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addNewProject.delay(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id, branch=branch, lang_code=settings.LANGUAGE_CODE)
            return HttpResponseRedirect(reverse('innov:main'))

    template = loader.get_template('Innov/addForm.html')
    context = RequestContext(request, {'gallery': gallery, 'photos': photos, 'form': form, 'pages': pages,
                                       'currentBranch': currentBranch, 'branches': branches,
                                       'currency_slots': currency_slots})
    newsPage = template.render(context)


    return newsPage




def _getValues(request):

    values = {}
    values['NAME'] = request.POST.get('NAME', "")
    values['PRODUCT_NAME'] = request.POST.get('PRODUCT_NAME', "")
    values['COST'] = request.POST.get('COST', "")
    values['CURRENCY'] = request.POST.get('CURRENCY', "")
    values['TARGET_AUDIENCE'] = request.POST.get('TARGET_AUDIENCE', "")
    values['RELEASE_DATE'] = request.POST.get('RELEASE_DATE', "")
    values['SITE_NAME'] = request.POST.get('SITE_NAME', "")
    values['KEYWORD'] = request.POST.get('KEYWORD', "")
    values['DETAIL_TEXT'] = request.POST.get('DETAIL_TEXT', "")
    values['BUSINESS_PLAN'] = request.POST.get('BUSINESS_PLAN', "")
    values['DOCUMENT_1'] = request.FILES.get('DOCUMENT_1', "")

    return values


