from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response, get_object_or_404
from appl.models import *
from django.http import HttpResponseRedirect, HttpResponse
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

def get_companies_list(request, page=1, item_id=None, my=None, slug=None):
    #if slug and not Value.objects.filter(item=item_id, attr__title='SLUG', title=slug).exists():
     #    slug = Value.objects.get(item=item_id, attr__title='SLUG').title
      #   return HttpResponseRedirect(reverse('companies:detail',  args=[slug]))
    cabinetValues = func.getB2BcabinetValues(request)


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
        newsPage = _companiesDetailContent(request, item_id)

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
            'item_id': item_id
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

    if not my:
        filters, searchFilter = func.filterLive(request)

        sqs = func.getActiveSQS().models(Company)

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

            url_paginator = "companies:my_main_paginator"

            params = {}

        else:
            raise ObjectDoesNotExist('you need check company')


    attr = ('NAME', 'IMAGE', 'ADDRESS', 'SITE_NAME', 'TELEPHONE_NUMBER', 'FAX', 'INN', 'DETAIL_TEXT', 'SLUG')

    result = func.setPaginationForSearchWithValues(companies, *attr,  page_num=5, page=page)

    companyList = result[0]
    company_ids = [id for id in companyList.keys()]
    countries = Country.objects.filter(p2c__child__in=company_ids, p2c__type='dependence').values('p2c__child', 'pk')
    countries_id = [country['pk'] for country in countries]
    countriesList = Item.getItemsAttributesValues(("NAME", 'FLAG'), countries_id)
    country_dict = {}

    for country in countries:
        country_dict[country['p2c__child']] = country['pk']

    for id, company in companyList.items():
        toUpdate = {'COUNTRY_NAME': countriesList[country_dict[id]].get('NAME', [0]) if country_dict.get(id, 0) else [0],
                    'COUNTRY_FLAG': countriesList[country_dict[id]].get('FLAG', [0]) if country_dict.get(id, 0) else [0],
                    'COUNTRY_ID':  country_dict.get(id, 0)}
        company.update(toUpdate)

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

    return template.render(context)


def _companiesDetailContent(request, item_id):

    company = get_object_or_404(Company, pk=item_id)
    companyValues = company.getAttributeValues(*('NAME', 'DETAIL_TEXT', 'IMAGE', 'POSITION'))

    country = Country.objects.get(p2c__child=company, p2c__type='dependence').getAttributeValues(*('FLAG', 'NAME'))

    template = loader.get_template('Companies/detailContent.html')

    context = RequestContext(request, {'companyValues': companyValues, 'country': country, 'item_id': item_id})

    return template.render(context)


def _tabsNews(request, company, page=1):

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

    return render_to_response('Companies/tabNews.html', templateParams, context_instance=RequestContext(request))


def _tabsTenders(request, company, page=1):

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
    
    return render_to_response('Companies/tabTenders.html', templateParams, context_instance=RequestContext(request))

def _tabsExhibitions(request, company, page=1):


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

    return render_to_response('Companies/tabExhibitions.html', templateParams, context_instance=RequestContext(request))


def _tabsProducts(request, company, page=1):


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

    return render_to_response('Companies/tabProducts.html', templateParams, context_instance=RequestContext(request))

#TODO complete this view (Ilya)
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
    departmentToAdd = request.POST.get('departmentName', '')

    if len(departmentToAdd):
        obj_dep = Department.objects.create(title=departmentToAdd, create_user=request.user)
        obj_dep.setAttributeValue({'NAME': departmentToAdd}, request.user)
        Relationship.setRelRelationship(Company.objects.get(pk=company), obj_dep, request.user, type='hierarchy')
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

#TODO complete this view (Ilya)
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
        dep_lst = list(Department.objects.filter(c2p__parent=company, c2p__type='hierarchy').values_list('pk', flat=True))
        if len(dep_lst) == 0:
            dep_lst = comp.community.pk # if Company w/o Departments

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
        'newsPage': newsPage,
        'current_company':current_company,
        'current_section': current_section,
        'cabinetValues': cabinetValues
    }

    return render_to_response('Companies/index.html', templatePrarams, context_instance=RequestContext(request))


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
        Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
        pages = Page(request.POST, request.FILES, prefix="pages")

        values = _getValues(request)
        branch = request.POST.get('BRANCH', "")

        form = ItemForm('Company', values=values)
        form.clean()

        if form.is_valid() and pages.is_valid():

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

        Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
        pages = Page(request.POST, request.FILES, prefix="pages", parent_id=item_id)
        pages = pages.queryset

        form = ItemForm('Company', id=item_id)

    if request.POST:
        user = request.user
        Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
        pages = Page(request.POST, request.FILES, prefix="pages")


        values = _getValues(request)
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
        'pages': pages,
        'company': company,
        'choosen_country': choosen_country,
        'countries': countries,
        'choosen_tpp': choosen_tpp,
        'tpp': tpp
    }

    context = RequestContext(request, templateParams)
    newsPage = template.render(context)

    return newsPage


def _getValues(request):
    values = {}

    values['ANONS'] = request.POST.get('ANONS', "")
    values['NAME'] = request.POST.get('NAME', "")
    values['IMAGE'] = request.FILES.get('IMAGE', "")
    values['ADDRESS'] = request.POST.get('ADDRESS', "")
    values['SITE_NAME'] = request.POST.get('SITE_NAME', "")
    values['TELEPHONE_NUMBER'] = request.POST.get('TELEPHONE_NUMBER', "")
    values['FAX'] = request.POST.get('FAX', "")
    values['INN'] = request.POST.get('INN', "")
    values['DETAIL_TEXT'] = request.POST.get('DETAIL_TEXT', "")
    values['SLOGAN'] = request.POST.get('SLOGAN', "")
    values['EMAIL'] = request.POST.get('EMAIL', "")
    values['KEYWORD'] = request.POST.get('KEYWORD', "")
    values['DIRECTOR'] = request.POST.get('DIRECTOR', "")
    values['KPP'] = request.POST.get('KPP', "")
    values['OKPO'] = request.POST.get('OKPO', "")
    values['OKATO'] = request.POST.get('OKATO', "")
    values['OKVED'] = request.POST.get('OKVED', "")
    values['ACCOUNTANT'] = request.POST.get('ACCOUNTANT', "")
    values['ACCOUNT_NUMBER'] = request.POST.get('ACCOUNT_NUMBER', "")
    values['BANK_DETAILS'] = request.POST.get('BANK_DETAILS', "")

    return values
