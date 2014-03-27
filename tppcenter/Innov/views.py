from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response, get_object_or_404
from appl.models import *
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
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


    if item_id:
       if not Item.active.get_active().filter(pk=item_id).exists():
         return HttpResponseNotFound()

    current_company = request.session.get('current_company', False)
    description = ''
    title = ''
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
       title = result[2]
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
            'description': description,
            'title': title
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

    if not my and not request.user.is_authenticated():
        if query.find('sortField') == -1 and query.find('order') == -1 and query.find('filter') == -1:
            cached = cache.get(cache_name)

    if not cached:

        q = request.GET.get('q', '')

        if not my:
            filters, searchFilter = func.filterLive(request)

            sqs = func.getActiveSQS().models(InnovationProject)

            if len(searchFilter) > 0:
                sqs = sqs.filter(searchFilter)

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

                if q != '':
                    innov_projects = innov_projects.filter(SQ(title=q) | SQ(text=q))

                innov_projects.order_by('-obj_create_date')

                url_paginator = "innov:my_main_paginator"
                params = {}

            else: #TODO Jenya do block try
                raise ObjectDoesNotExist('you need check company')

        result = func.setPaginationForSearchWithValues(innov_projects, *('NAME', 'SLUG'), page_num=7, page=page)

        innovList = result[0]
        innov_ids = [id for id in innovList.keys()]


        branches = Branch.objects.filter(p2c__child__in=innov_ids).values('p2c__child', 'pk')
        branches_ids = [branch['pk'] for branch in branches]
        branchesList = Item.getItemsAttributesValues(("NAME"), branches_ids)

        branches_dict = {}

        for branch in branches:
            branches_dict[branch['p2c__child']] = branch['pk']



        for id, innov in innovList.items():

            toUpdate = {
                'BRANCH_NAME': branchesList[branches_dict[id]].get('NAME', 0) if branches_dict.get(id, 0) else [0],
                'BRANCH_ID': branches_dict.get(id, 0),
            }

            innov.update(toUpdate)

        func.addDictinoryWithCountryAndOrganizationToInnov(innov_ids, innovList)

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

        if not my and not request.user.is_authenticated():
            if query.find('sortField') == -1 and query.find('order') == -1 and query.find('filter') == -1:
                cache.set(cache_name, rendered)

    else:
        rendered = cache.get(cache_name)
    return rendered



def _innovDetailContent(request, item_id):


    cache_name = "detail_%s" % item_id
    description_cache_name = "description_%s" % item_id
    cached = cache.get(cache_name)

    if not cached:

        innov = get_object_or_404(InnovationProject, pk=item_id)

        attr = ('NAME', 'PRODUCT_NAME', 'COST', 'REALESE_DATE', 'BUSINESS_PLAN', 'CURRENCY', 'DOCUMENT_1', 'DETAIL_TEXT')

        innovValues = innov.getAttributeValues(*attr)
        description = innovValues.get('DETAIL_TEXT', False)[0] if innovValues.get('DETAIL_TEXT', False) else ""
        description = func.cleanFromHtml(description)
        title = innovValues.get('NAME', False)[0] if innovValues.get('NAME', False) else ""
        photos = Gallery.objects.filter(c2p__parent=item_id)

        additionalPages = AdditionalPages.objects.filter(c2p__parent=item_id)

        try:
            branch = Branch.objects.get(p2c__child=item_id)
            branchValues = branch.getAttributeValues('NAME')
            innovValues.update({'BRANCH_NAME': branchValues, 'BRANCH_ID': branch.id})
        except ObjectDoesNotExist:
            innovValues.update({'BRANCH_NAME': [0], 'BRANCH_ID': 0})


        func.addToItemDictinoryWithCountryAndOrganization(innov.id, innovValues, withContacts=True)


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
            'cabinetUpdate': cabinetUpdate,
            'item_id': item_id
        }

        context = RequestContext(request, templateParams)
        rendered = template.render(context)
        cache.set(cache_name, rendered, 60*60*24*7)
        cache.set(description_cache_name, (description, title), 60*60*24*7)

    else:
        rendered = cache.get(cache_name)
        result = cache.get(description_cache_name)
        description = result[0]
        title = result[1]

    return rendered, description, title



@login_required(login_url='/login/')
def innovForm(request, action, item_id=None):
    if item_id:
       if not InnovationProject.active.get_active().filter(pk=item_id).exists():
         return HttpResponseNotFound

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
        'formContent': newsPage,
        'current_company':current_company,
        'current_section': current_section,
        'cabinetValues': cabinetValues
    }

    return render_to_response('forms.html', templateParams, context_instance=RequestContext(request))

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
    pages = None
    if request.POST:

        user = request.user

        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=5, fields=("photo",))
        gallery = Photo(request.POST, request.FILES)

        Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
        pages = Page(request.POST, request.FILES, prefix="pages")
        if getattr(pages, 'new_objects', False):
           pages = pages.new_objects

        values = {}
        values.update(request.POST)
        values.update(request.FILES)

        branch = request.POST.get('BRANCH', "")

        form = ItemForm('InnovationProject', values=values)
        form.clean()

        if gallery.is_valid() and form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addNewProject.delay(request.POST, request.FILES, user, settings.SITE_ID, branch=branch, current_company=current_company, lang_code=settings.LANGUAGE_CODE)
            return HttpResponseRedirect(reverse('innov:main'))


    template = loader.get_template('Innov/addForm.html')
    context = RequestContext(request, {'form': form, 'branches': branches, 'currency_slots': currency_slots, 'pages': pages})
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
    if getattr(pages, 'new_objects', False):
        pages = pages.new_objects
    else:
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

        values = {}
        values.update(request.POST)
        values.update(request.FILES)

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






