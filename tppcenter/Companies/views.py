from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response, get_object_or_404
from appl.models import *
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from core.models import Item
from appl import func
from django.forms.models import modelformset_factory
from tppcenter.forms import ItemForm, BasePages
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from core.tasks import addNewCompany
from haystack.query import SQ, SearchQuerySet
import json
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from itertools import chain
from django.core.cache import cache

def get_companies_list(request, page=1, item_id=None, my=None, slug=None):
    #if slug and not Value.objects.filter(item=item_id, attr__title='SLUG', title=slug).exists():
     #    slug = Value.objects.get(item=item_id, attr__title='SLUG').title
      #   return HttpResponseRedirect(reverse('companies:detail',  args=[slug]))
    if item_id:
       if not Item.active.get_active().filter(pk=item_id).exists():
         return HttpResponseNotFound

    cabinetValues = func.getB2BcabinetValues(request)

    description = ""
    title = ""
    current_company = request.session.get('current_company', False)

    if current_company:
        current_company = Organization.objects.get(pk=current_company).getAttributeValues("NAME")


    styles = [
        settings.STATIC_URL + 'tppcenter/css/news.css',
        settings.STATIC_URL + 'tppcenter/css/company.css',
        settings.STATIC_URL + 'tppcenter/css/tpp.reset.css'
    ]

    scripts = []

    if not item_id:
        try:
            newsPage = _companiesContent(request, page=page, my=my)

        except ObjectDoesNotExist:
            newsPage = func.emptyCompany()
    else:
        result = _companiesDetailContent(request, item_id)
        newsPage = result[0]
        description = result[1]
        title = result[2]
    if not request.is_ajax():

        current_section = _("Companies")

        templateParams = {
            'current_section': current_section,
            'newsPage': newsPage,
            'scripts': scripts,
            'styles': styles,
            'search': request.GET.get('q', ''),
            'current_company': current_company,
            'addNew': reverse('companies:add'),
            'cabinetValues': cabinetValues,
            'item_id': item_id,
            'description': description,
            'title': title
        }

        return render_to_response("Companies/index.html", templateParams, context_instance=RequestContext(request))

    else:

        serialize = {
            'styles': styles,
            'scripts': scripts,
            'content': newsPage
        }

        return HttpResponse(json.dumps(serialize))


def _companiesContent(request, page=1, my=None):
    cached = False
    cache_name = "company_list_result_page_%s" % (page)
    query = request.GET.urlencode()

    if not my and not request.user.is_authenticated():
        if query.find('sortField') == -1 and query.find('order') == -1 and query.find('filter') == -1:
            cached = cache.get(cache_name)

    if not cached:

        q = request.GET.get('q', '')

        if not my:
            filters, searchFilter = func.filterLive(request)

            sqs = func.getActiveSQS().models(Company)

            if len(searchFilter) > 0:
                sqs = sqs.filter(searchFilter)

            if q != '':
                sqs = sqs.filter(title=q)

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

            companies = sqs.order_by(*order)

            url_paginator = "companies:paginator"

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
                companies = SearchQuerySet().models(Company).filter(SQ(tpp=current_organization) | SQ(id=current_organization))

                if q != '':
                    companies = companies.filter(title=q)

                url_paginator = "companies:my_main_paginator"

                params = {}

            else:
                raise ObjectDoesNotExist('you need check company')


        attr = ('NAME', 'IMAGE', 'ADDRESS', 'SITE_NAME', 'TELEPHONE_NUMBER', 'FAX', 'INN', 'DETAIL_TEXT', 'SLUG')

        result = func.setPaginationForSearchWithValues(companies, *attr,  page_num=5, page=page)

        companyList = result[0]
        company_ids = [id for id in companyList.keys()]
        func.addDictinoryWithCountryToCompany(company_ids,companyList)

        page = result[1]
        paginator_range = func.getPaginatorRange(page)


        template = loader.get_template('Companies/contentPage.html')

        templateParams = {
            'companyList': companyList,
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



def _companiesDetailContent(request, item_id):
    cache_name = "detail_%s" % item_id
    description_cache_name = "description_%s" % item_id
    query = request.GET.urlencode()
    cached = cache.get(cache_name)

    if not cached:
        company = get_object_or_404(Company, pk=item_id)
        companyValues = company.getAttributeValues(*('NAME', 'DETAIL_TEXT', 'IMAGE', 'POSITION', 'ADDRESS',
                                                     'TELEPHONE_NUMBER', 'FAX', 'EMAIL', 'SITE_NAME'))
        description = companyValues.get('DETAIL_TEXT', False)[0] if companyValues.get('DETAIL_TEXT', False) else ""
        description = func.cleanFromHtml(description)
        title = companyValues.get('NAME', False)[0] if companyValues.get('NAME', False) else ""

        country = Country.objects.get(p2c__child=company, p2c__type='dependence').getAttributeValues(*('FLAG', 'NAME'))

        template = loader.get_template('Companies/detailContent.html')

        context = RequestContext(request, {'companyValues': companyValues, 'country': country, 'item_id': item_id})
        rendered = template.render(context)
        cache.set(cache_name, rendered, 60*60*24*7)
        cache.set(description_cache_name, (description, title), 60*60*24*7)

    else:
        rendered = cache.get(cache_name)
        result = cache.get(description_cache_name)
        description = result[0]
        title = result[1]

    return rendered, description, title


def _tabsNews(request, company, page=1):
    cache_name = "News_tab_company_%s_page_%s" % (company, page)
    cached = cache.get(cache_name)

    if not cached:
        news = func.getActiveSQS().models(News).filter(company=company)
        attr = ('NAME', 'IMAGE', 'DETAIL_TEXT', 'SLUG')

        result = func.setPaginationForSearchWithValues(news, *attr, page_num=5, page=page)

        newsList = result[0]

        page = result[1]
        paginator_range = func.getPaginatorRange(page)

        url_paginator = "companies:tab_news_paged"

        templateParams = {
            'newsList': newsList,
            'page': page,
            'paginator_range': paginator_range,
            'url_paginator': url_paginator,
            'url_parameter': company
        }
        cache.set(cache_name, templateParams, 60*60)
    else:
        templateParams = cached

    return render_to_response('Companies/tabNews.html', templateParams, context_instance=RequestContext(request))


def _tabsTenders(request, company, page=1):
    cache_name = "Tenders_tab_company_%s_page_%s" % (company, page)
    cached = cache.get(cache_name)

    if not cached:
        tenders = func.getActiveSQS().models(Tender).filter(company=company)

        attr = ('NAME', 'START_EVENT_DATE', 'END_EVENT_DATE', 'COST', 'CURRENCY', 'SLUG')

        result = func.setPaginationForSearchWithValues(tenders, *attr, page_num=5, page=page)


        tendersList = result[0]

        page = result[1]
        paginator_range = func.getPaginatorRange(page)

        url_paginator = "companies:tab_tenders_paged"

        templateParams = {
            'tendersList': tendersList,
            'page': page,
            'paginator_range': paginator_range,
            'url_paginator': url_paginator,
            'url_parameter': company,


        }
        cache.set(cache_name, templateParams, 60*60)
    else:
        templateParams = cached
    
    return render_to_response('Companies/tabTenders.html', templateParams, context_instance=RequestContext(request))

def _tabsExhibitions(request, company, page=1):
    cache_name = "Exhibitions_tab_company_%s_page_%s" % (company, page)
    cached = cache.get(cache_name)

    if not cached:
        exhibition = func.getActiveSQS().models(Exhibition).filter(company=company)
        attr = ('NAME', 'SLUG', 'START_EVENT_DATE', 'END_EVENT_DATE', 'CITY')

        result = func.setPaginationForSearchWithValues(exhibition, *attr, page_num=5, page=page)

        exhibitionList = result[0]

        page = result[1]
        paginator_range = func.getPaginatorRange(page)

        url_paginator = "companies:tab_exhibitions_paged"

        templateParams = {
            'exhibitionList': exhibitionList,
            'page': page,
            'paginator_range': paginator_range,
            'url_paginator': url_paginator,
            'url_parameter': company
        }
        cache.set(cache_name, templateParams, 60*60)
    else:
        templateParams = cached

    return render_to_response('Companies/tabExhibitions.html', templateParams, context_instance=RequestContext(request))


def _tabsProducts(request, company, page=1):
    cache_name = "Products_tab_company_%s_page_%s" % (company, page)
    cached = cache.get(cache_name)

    if not cached:
        products = func.getActiveSQS().models(Product).filter(company=company)
        attr = ('NAME', 'IMAGE', 'COST', 'CURRENCY', 'SLUG', 'DETAIL_TEXT')

        result = func.setPaginationForSearchWithValues(products, *attr, page_num=5, page=page)


        productsList = result[0]

        page = result[1]
        paginator_range = func.getPaginatorRange(page)

        url_paginator = "companies:tab_products_paged"

        templateParams = {
            'productsList': productsList,
            'page': page,
            'paginator_range': paginator_range,
            'url_paginator': url_paginator,
            'url_parameter': company
        }
        cache.set(cache_name, templateParams, 60*60)
    else:
        templateParams = cached

    return render_to_response('Companies/tabProducts.html', templateParams, context_instance=RequestContext(request))

def _tabsStructure(request, company, page=1):
    '''
        Show content of the Company-details-structure panel
    '''
    #check if there Department for deletion
    departmentForDeletion = request.POST.get('departmentID', 0)

    try:
        departmentForDeletion = int(departmentForDeletion)
    except ValueError:
        departmentForDeletion = 0

    if departmentForDeletion > 0:
        Department.objects.filter(pk=departmentForDeletion).delete()

    #check if there Department for adding
    departmentToChange = request.POST.get('departmentName', '')

    if len(departmentToChange):
        #if update department we receive previous name
        prevDepName = request.POST.get('prevDepName', '')
        try:
            #check is there department with 'old' name
            obj_dep = Department.objects.get(item2value__attr__title="NAME", item2value__title=prevDepName)
        except:
            obj_dep = Department.objects.create(title=departmentToChange, create_user=request.user)
            Relationship.setRelRelationship(Company.objects.get(pk=company), obj_dep, request.user, type='hierarchy')

        obj_dep.setAttributeValue({'NAME': departmentToChange}, request.user)
        obj_dep.reindexItem()

    departments = func.getActiveSQS().models(Department).filter(company=company).order_by('text')
    attr = ('NAME', 'SLUG')

    departmentsList, page = func.setPaginationForSearchWithValues(departments, *attr, page_num=10, page=page)

    paginator_range = func.getPaginatorRange(page)
    url_paginator = "companies:tab_structure_paged"

    templateParams = {
        'departmentsList': departmentsList,
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'url_parameter': company,
    }

    return render_to_response('Companies/tabStructure.html', templateParams, context_instance=RequestContext(request))

def _tabsStaff(request, company, page=1):
    '''
        Show content of the Company-details-staff panel
    '''
    # get Cabinet ID if user should be detach from Organization
    cabinetToDetach = request.POST.get('cabinetID', 0)

    try:
        cabinetToDetach = int(cabinetToDetach)
    except ValueError:
        cabinetToDetach = 0

    if cabinetToDetach > 0:
        userToDetach = User.objects.get(cabinet__pk=cabinetToDetach)
        comp = Company.objects.get(pk=company)
        #create list of pk for Company's Organizations
        cab_lst = list(Department.objects.filter(c2p__parent=company, c2p__type='hierarchy').values_list('community__user__cabinet__pk', flat=True))
        cab_lst += list(Group.objects.filter(name=comp.community.name).values_list('user__cabinet__pk', flat=True))
        # create cross list for Cabinet IDs and Organization IDs - list of tuples
        correlation = list(Organization.objects.filter(community__user__cabinet__pk__in=cab_lst).values_list('pk', 'community__user__cabinet__pk'))

        for t in correlation:
            if t[1] == cabinetToDetach:
                comp = Organization.objects.get(pk=t[0])
                communityGroup = Group.objects.get(pk=comp.community_id)
                communityGroup.user_set.remove(userToDetach)

        return HttpResponse('Ok')
    else:
        comp = Company.objects.get(pk=company)
        cab_lst = list(Department.objects.filter(c2p__parent=company, c2p__type='hierarchy').values_list('community__user__cabinet__pk', flat=True))
        cab_lst += list(Group.objects.filter(name=comp.community.name).values_list('user__cabinet__pk', flat=True))
        attr = ('USER_FIRST_NAME', 'USER_MIDDLE_NAME', 'USER_LAST_NAME', 'EMAIL', 'IMAGE', 'SLUG')

        cabinets = Cabinet.objects.filter(pk__in=cab_lst)
        workersList, page = func.setPaginationForSearchWithValues(cabinets, *attr, page_num=10, page=page)

        # add Department, Joined_date and Status fields
        dep_lst = tuple(Organization.objects.filter(community__user__cabinet__pk__in=cab_lst).values_list('pk', flat=True))
        org_lst = Item.getItemsAttributesValues(('NAME',), dep_lst)
        #create correlation list between Organization IDs and Cabinet IDs
        correlation = list(Organization.objects.filter(community__user__cabinet__pk__in=cab_lst).values_list('pk', 'community__user__cabinet__pk'))

        for cab_id, cab_att in workersList.items(): #get Cabinet ID
            for t in correlation: #lookup into corelation list
                if t[1] == cab_id: #if Cabinet ID then...
                    dep_id = t[0] #...get Organization ID
                    for org_id, org_attr in org_lst.items(): #from OrderedDict...
                        if org_id == dep_id:    #if found the same Organization ID then...
                            #... set additional attributes for Users (Cabinets) befor sending to web form
                            cab_att['DEPARTMENT'] = org_attr['NAME']
                            cab_att['JOINED_DATE'] = org_attr['CREATE_DATE']
                            cab_att['STATUS'] = ['Active']
                            break

        paginator_range = func.getPaginatorRange(page)
        url_paginator = "companies:tab_staff_paged"

        #create full list of Company's departments
        departments = func.getActiveSQS().models(Department).filter(company=company).order_by('text')

        dep_lst = [dep.pk for dep in departments]

        if len(dep_lst) == 0:
            departmentsList = []
        else:
            departmentsList = Item.getItemsAttributesValues(('NAME',), dep_lst)

        templateParams = {
            'workersList': workersList,
            'departmentsList': departmentsList, #list for add user form
            'page': page,
            'paginator_range': paginator_range,
            'url_paginator': url_paginator,
            'url_parameter': company,
        }

        return render_to_response('Companies/tabStaff.html', templateParams, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def companyForm(request, action, item_id=None):
    if item_id:
       if not Company.active.get_active().filter(pk=item_id).exists():
         return HttpResponseNotFound

    cabinetValues = func.getB2BcabinetValues(request)

    current_company = request.session.get('current_company', False)
    if current_company:
        current_company = Organization.objects.get(pk=current_company).getAttributeValues("NAME")

    current_section = _("Companies")

    if action == 'add':
        newsPage = addCompany(request)
    else:
        newsPage = updateCompany(request, item_id)

    if isinstance(newsPage, HttpResponseRedirect) or isinstance(newsPage, HttpResponse):
        return newsPage

    templatePrarams = {
        'formContent': newsPage,
        'current_company': current_company,
        'current_section': current_section,
        'cabinetValues': cabinetValues
    }

    return render_to_response('forms.html', templatePrarams, context_instance=RequestContext(request))


def addCompany(request):
    user = request.user

    user_groups = user.groups.values_list('name', flat=True)

    if not 'Company Creator' in user_groups:
        return func.permissionDenied()

    form = None

    branches = Branch.objects.all()
    branches_ids = [branch.id for branch in branches]
    branches = Item.getItemsAttributesValues(("NAME",), branches_ids)

    countries = func.getItemsList("Country", 'NAME')
    tpp = func.getItemsList("Tpp", 'NAME')


    if request.POST:


        values = {}
        values.update(request.POST)
        values.update(request.FILES)
        branch = request.POST.get('BRANCH', "")

        form = ItemForm('Company', values=values)
        form.clean()

        if form.is_valid():

            func.notify("item_creating", 'notification', user=request.user)

            addNewCompany.delay(request.POST, request.FILES, user, settings.SITE_ID,
                                branch=branch, lang_code=settings.LANGUAGE_CODE)

            return HttpResponseRedirect(reverse('companies:main'))

    template = loader.get_template('Companies/addForm.html')

    context = RequestContext(request, {'form': form, 'branches': branches, 'countries': countries, 'tpp': tpp})

    newsPage = template.render(context)

    return newsPage


def updateCompany(request, item_id):

    item = Organization.objects.get(pk=item_id)

    perm_list = item.getItemInstPermList(request.user)

    if 'change_company' not in perm_list:
        return func.permissionDenied()
    try:
        choosen_country = Country.objects.get(p2c__child__id=item_id)
    except ObjectDoesNotExist:
        choosen_country = ""
    try:
        choosen_tpp = Tpp.objects.get(p2c__child__id=item_id)
    except ObjectDoesNotExist:
        choosen_tpp = ""

    countries = func.getItemsList("Country", 'NAME')
    tpp = func.getItemsList("Tpp", 'NAME')

    company = Company.objects.get(pk=item_id)

    if request.method != 'POST':
        branches = Branch.objects.all()
        branches_ids = [branch.id for branch in branches]
        branches = Item.getItemsAttributesValues(("NAME",), branches_ids)

        try:
            currentBranch = Branch.objects.get(p2c__child=item_id)
        except Exception:
            currentBranch = ""



        form = ItemForm('Company', id=item_id)

    if request.POST:
        user = request.user



        values = {}
        values.update(request.POST)
        values.update(request.FILES)
        branch = request.POST.get('BRANCH', "")

        form = ItemForm('Company', values=values, id=item_id)
        form.clean()

        if form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addNewCompany.delay(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id, branch=branch, lang_code=settings.LANGUAGE_CODE)
            return HttpResponseRedirect(reverse('companies:main'))


    template = loader.get_template('Companies/addForm.html')

    templateParams = {
        'form': form,
        'branches': branches,
        'currentBranch': currentBranch,
        'company': company,
        'choosen_country': choosen_country,
        'countries': countries,
        'choosen_tpp': choosen_tpp,
        'tpp': tpp
    }

    context = RequestContext(request, templateParams)
    newsPage = template.render(context)

    return newsPage


