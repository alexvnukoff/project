import datetime
import json
import logging

from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.forms.models import modelformset_factory
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound, HttpResponseBadRequest, \
    HttpResponseNotAllowed
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _
from django.utils.timezone import now
from django.utils.translation import trans_real
from haystack.backends import SQ

from appl import func
from appl.models import Company, Product, Exhibition, Country, News, Tender, BusinessProposal, Organization, Department, \
                        Branch, Tpp, InnovationProject, Cabinet, Vacancy, Gallery, AdditionalPages
from core.models import Item, Relationship, User, Group
from core.tasks import addNewCompany
from core.amazonMethods import add
from tppcenter.cbv import ItemDetail, ItemsList
from tppcenter.forms import ItemForm, BasePages
from tppcenter.Messages.views import addMessages


logger = logging.getLogger('django.request')

class get_companies_list(ItemsList):

    #pagination url
    url_paginator = "companies:paginator"
    url_my_paginator = "companies:my_main_paginator"

    current_section = _("Companies")
    addUrl = 'companies:add'

    #Lists of required scripts and styles for ajax request
    styles = [
        settings.STATIC_URL + 'tppcenter/css/news.css',
        settings.STATIC_URL + 'tppcenter/css/company.css',
        settings.STATIC_URL + 'tppcenter/css/tpp.reset.css'
    ]

    #allowed filter list
    filterList = ['tpp', 'country', 'branch']

    model = Company

    def ajax(self, request, *args, **kwargs):
        self.template_name = 'Companies/contentPage.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'Companies/index.html'

    def _get_my(self):

        return SQ(django_id__gt=0)

    def get_queryset(self):

        if self.request.user.is_authenticated() and  self.is_my():
            cab = Cabinet.objects.get(user=self.request.user.pk)
            self.querysetDB = True
            return Company.active.get_active().filter(Q(create_user=self.request.user) |
                                                               Q(p2c__child__p2c__child__p2c__child=cab.pk)).distinct()
        else:
            return super(get_companies_list, self).get_queryset()

class get_company_detail(ItemDetail):

    model = Company
    template_name = 'Companies/detailContent.html'

    current_section = _("Companies")
    addUrl = 'companies:add'

    def _get_payed_status(self):

        company = None
        result = {
            'SHOW_PAYMENT_BUTTON': False
        }

        try:
            if self.request.user.is_commando or self.request.user.is_admin:
                company = Company.objects.get(pk=self.object.pk)
            else:
                cab = Cabinet.objects.get(user=self.request.user)
                company = Company.objects.get(pk=self.object.pk, p2c__child__p2c__child__p2c__child=cab)
        except ObjectDoesNotExist:
            return result

        if not company.paid_till_date:
            return result

        days_till_end = (company.paid_till_date - datetime.datetime.now().date()).days

        if days_till_end <= settings.NOTIFICATION_BEFORE_END_DATE and days_till_end > 0:
            result['SHOW_PAYMENT_BUTTON'] = True
            result['DAYS_BEFORE_END'] = days_till_end
        elif(days_till_end > 0):
            result['SHOW_PAYMENT_BUTTON'] = False
        else:
            company.end_date = now()
            company.save()
            result['SHOW_PAYMENT_BUTTON'] = True
            result['DAYS_BEFORE_END'] = 0

        return result

    def get_context_data(self, **kwargs):
        context = super(get_company_detail, self).get_context_data(**kwargs)

        context.update({
            'photos': self._get_gallery(),
            'additionalPages': self._get_additional_pages(),
        })

        if self.request.user.is_authenticated():
            context.update(self._get_payed_status())

        return context



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

def _tabsProposals(request, company, page=1):

        products = func.getActiveSQS().models(BusinessProposal).filter(company=company)
        attr = ('NAME', 'SLUG')

        result = func.setPaginationForSearchWithValues(products, *attr, page_num=5, page=page)


        proposalList = result[0]

        page = result[1]
        paginator_range = func.getPaginatorRange(page)

        url_paginator = "companies:tab_proposal_paged"

        templateParams = {
            'proposalList': proposalList,
            'page': page,
            'paginator_range': paginator_range,
            'url_paginator': url_paginator,
            'url_parameter': company
        }


        return render_to_response('Companies/tabProposal.html', templateParams, context_instance=RequestContext(request))


def _tabsInnovs(request, company, page=1):

        products = func.getActiveSQS().models(InnovationProject).filter(company=company)
        attr = ('NAME', 'COST', 'CURRENCY', 'SLUG')

        result = func.setPaginationForSearchWithValues(products, *attr, page_num=5, page=page)


        innovList = result[0]

        page = result[1]
        paginator_range = func.getPaginatorRange(page)

        url_paginator = "companies:tab_innov_paged"

        templateParams = {
            'innovList': innovList,
            'page': page,
            'paginator_range': paginator_range,
            'url_paginator': url_paginator,
            'url_parameter': company
        }

        return render_to_response('Companies/tabInnov.html', templateParams, context_instance=RequestContext(request))


@transaction.atomic
def _tabsStructure(request, company, page=1):
    '''
        Show content of the Company-details-structure panel
    '''

    comp = get_object_or_404(Company, pk=company)
    permissionsList = comp.getItemInstPermList(request.user)

    if request.is_ajax() and request.user.is_authenticated():

        try:
            id = int(request.POST.get("id", 0))
        except ValueError:
            id = 0

        name = request.POST.get('name', '').strip()
        action = request.POST.get("action", None)

        if "change_company" not in permissionsList and action is not None: # Error
            return HttpResponseBadRequest()

        if action == "add" and len(name) > 0:

            if id == 0: # new department
                obj_dep = Department.objects.create(title=name, create_user=request.user)
                Relationship.setRelRelationship(comp, obj_dep, request.user, type='hierarchy')
                obj_dep.setAttributeValue({'NAME': name}, request.user)

                obj_dep.reindexItem()
            else: # new vacancy
                department = get_object_or_404(Department, pk=id)
                vac = Vacancy.objects.create(title='VACANCY_FOR_ORGANIZATION_ID:'+str(department.pk), create_user=request.user)
                vac.setAttributeValue({'NAME': name}, request.user)

                Relationship.setRelRelationship(department, vac, request.user, type='hierarchy')

                vac.reindexItem()

        elif action == "edit" and id > 0 and len(name) > 0:

            try:
                obj = Department.objects.get(pk=id)
            except ObjectDoesNotExist:
                obj = get_object_or_404(Vacancy, pk=id)

            obj.setAttributeValue({'NAME': name}, request.user)

            obj.reindexItem()

        elif action == "remove" and id > 0:
            try:
                obj = Department.objects.get(pk=id)
                Item.hierarchy.deleteTree(obj.pk)
            except ObjectDoesNotExist:
                obj = get_object_or_404(Vacancy, pk=id)

            obj.delete()

    departments = func.getActiveSQS().models(Department).filter(company=company).order_by('text')

    paginator = Paginator(departments, 10)
    departments = paginator.page(page)
    paginator_range = func.getPaginatorRange(departments)
    url_paginator = "companies:tab_structure_paged"
    departmentsDict = {}
    departmentsList = []

    for department in departments.object_list:
        department.vacancyList = []
        departmentsDict[int(department.pk)] = department
        departmentsList.append(department.pk)

    vacancies = func.getActiveSQS().models(Vacancy).filter(company=company, department__in=departmentsList).order_by('text')

    for vacancy in vacancies:
        departmentsDict[int(vacancy.department)].vacancyList.append(vacancy)

    templateParams = {
        'permissionsList': permissionsList,
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'url_parameter': company,
        'departments': departmentsDict,
        'item_pk': company
    }

    return render_to_response('Companies/tabStructure.html', templateParams, context_instance=RequestContext(request))

def _tabsStaff(request, company, page=1):
    '''
        Show content of the Company-details-staff panel
    '''
    # get Cabinet ID if user should be detach from Organization
    organization = get_object_or_404(Company, pk=company)
    permissionsList = organization.getItemInstPermList(request.user)

    if request.is_ajax() and request.user.is_authenticated():

        action = request.POST.get('action', False)

        action = action if action else request.GET.get('action', None)

        if "add_cabinet" not in permissionsList and action is not None: # Error
            return HttpResponseBadRequest()

        if action == "department":
            departments = [{'name': _("Select department"), "value": ""}]

            for department in func.getActiveSQS().models(Department).filter(company=company).order_by('text'):
                departments.append({"name": department.text, "value": department.pk})

            return HttpResponse(json.dumps(departments))

        elif action == "vacancy":

            department = int(request.GET.get("department", 0))

            if department <= 0:
                return HttpResponseBadRequest()

            vacancies = [{'name': _("Select vacancy"), "value": ""}]

            for vacancy in func.getActiveSQS().models(Vacancy).filter(company=company).order_by('text'):
                if vacancy.department == department:
                    vacancies.append({"name": vacancy.text, "value": vacancy.pk})

            return HttpResponse(json.dumps(vacancies))

        elif action == "add":

            user = request.POST.get('user', "").strip()
            department = int(request.POST.get('department', 0))
            vacancy = int(request.POST.get('vacancy', 0))

            if not user or department <= 0 or vacancy <= 0:
                return HttpResponseBadRequest()

            try:
                user = User.objects.get(email=user)
                department = Department.objects.get(pk=department, c2p__parent=company)
                vacancy = Vacancy.objects.get(pk=vacancy, c2p__parent=department)
            except ObjectDoesNotExist:
                return HttpResponseBadRequest(_('User not found'))

            # One user for vacancy
            if Cabinet.objects.filter(c2p__parent=vacancy.pk).exists():
                return HttpResponseBadRequest(_("The vacancy already have employee attached"))

            cab, res = Cabinet.objects.get_or_create(user=user, create_user=user)

            if res: # user exists but never logged in
                cab.setAttributeValue({
                                          'USER_FIRST_NAME': user.first_name,
                                          'USER_MIDDLE_NAME':'',
                                          'USER_LAST_NAME': user.last_name,
                                          'EMAIL': user.email
                }, user)
            elif Cabinet.objects.filter(pk=cab.pk, c2p__parent__c2p__parent__c2p__parent=company).exists():
                return HttpResponseBadRequest(_("The user already employed in your organization"))


            admin = int(request.POST.get('admin', 0))
            admin = True if admin != 0 else False

            if admin:
                user.is_manager = True
                user.save()

            Relationship.objects.get_or_create(parent=vacancy, child=cab, is_admin=admin, type='relation',
                                                create_user=user)
            cab.reindexItem()
            vacancy.reindexItem()

        elif action == "remove":
            cabinet = int(request.POST.get('id', 0))

            if cabinet > 0:

                cabinet = get_object_or_404(Cabinet, pk=cabinet)

                vacancy = get_object_or_404(Vacancy, p2c__child=cabinet.pk, c2p__parent__c2p__parent=company)

                Relationship.objects.filter(parent__c2p__parent__c2p__parent=company, child=cabinet,
                                                type='relation').delete()

                cabinet.reindexItem()
                vacancy.reindexItem()

    cabinets = Cabinet.objects.filter(c2p__parent__c2p__parent__c2p__parent=company).distinct()
    attr = ('USER_FIRST_NAME', 'USER_MIDDLE_NAME', 'USER_LAST_NAME', 'EMAIL', 'IMAGE', 'SLUG')
    workersList, page = func.setPaginationForItemsWithValues(cabinets, *attr, page_num=10, page=page)

    dep_lst = tuple(Department.objects.filter(c2p__parent=company).values_list('pk', flat=True))
    org_lst = Item.getItemsAttributesValues(('NAME',), dep_lst)
    correlation = list(Department.objects.filter(c2p__parent=company).values_list('pk', 'p2c__child__p2c__child'))

    for cab_id, cab_att in workersList.items(): #get Cabinet instance
        for t in correlation: #lookup into corelation list
            if t[1] == cab_id: #if Cabinet ID then...
                dep_id = t[0] #...get Organization ID
                for org_id, org_attr in org_lst.items(): #from OrderedDict...
                    if org_id == dep_id:    #if found the same Organization ID then...
                        #... set additional attributes for Users (Cabinets) before sending to web form
                        cab_att['DEPARTMENT'] = org_attr['NAME']

                        # check current User's activity
                        for cab in cabinets:
                            if cab.pk == cab_id:
                                if cab.user.is_authenticated():
                                    cab_att['STATUS'] = ['Active']
                                else:
                                    cab_att['STATUS'] = ['None']

                                break
                        break

    paginator_range = func.getPaginatorRange(page)
    url_paginator = "companies:tab_staff_paged"

    #create full list of Company's Departments
    departments = func.getActiveSQS().models(Department).filter(company=company).order_by('title_sort')

    #create list of Company's Vacancies
    vacancies = func.getActiveSQS().models(Vacancy).filter(company=company).order_by('text')

    vac_lst = [vac.pk for vac in vacancies]

    if len(vac_lst) == 0:
        vacanciesList = []
    else:
        vacanciesList = Item.getItemsAttributesValues(('NAME',), vac_lst)
        # correlation between Departments and Vacancies
        correlation = list(Department.objects.filter(c2p__parent=company).values_list('pk', 'p2c__child'))

        # add into Vacancy's attribute a new key 'DEPARTMENT_ID' with Department ID
        for vac_id, vac_att in vacanciesList.items(): #get Vacancy instance
            for t in correlation: #lookup into correlation list
                if t[1] == vac_id: #if Vacancy ID is equal then...
                    #... add a new key into Vacancy attribute dictionary
                    vac_att['DEPARTMENT_ID'] = [t[0]]
                    break

        correlation = list(Department.objects.filter(c2p__parent=company).values_list('p2c__child__p2c__child', 'p2c__child'))

        # add into worker's list attribute a new key 'VACANCY' with Vacancy ID
        for cab_id, cab_att in workersList.items(): #get Cabinet instance
            for t in correlation: #lookup into correlation list
                if t[0] == cab_id: #if Cabinet ID is equal then...
                    for vac_id, vac_attr in vacanciesList.items():
                        if t[1] == vac_id:
                            #... add a new key into User (Cabinet) attribute dictionary
                            cab_att['VACANCY'] = vac_attr['NAME']
                            break

    comp = Company.objects.get(pk=company)
    permissionsList = comp.getItemInstPermList(request.user)

    templateParams = {
        'workersList': workersList,
        'departmentsList': departments, #list for adding user form
        'vacanciesList': vacanciesList,     #list for adding user form
        'permissionsList': permissionsList,
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'url_parameter': company,
        'item_pk': company
    }

    return render_to_response('Companies/tabStaff.html', templateParams, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def companyForm(request, action, item_id=None):

    if item_id:
       if not Company.active.get_active().filter(pk=item_id).exists():
         return HttpResponseNotFound()

    current_section = _("Companies")

    newsPage = ''

    if action == 'delete':
        newsPage = deleteCompany(request, item_id)
    elif action == 'add':
        newsPage = addCompany(request)
    elif action == 'update':
        newsPage = updateCompany(request, item_id)

    if isinstance(newsPage, HttpResponseRedirect) or isinstance(newsPage, HttpResponse):
        return newsPage

    templatePrarams = {
        'formContent': newsPage,
        'current_section': current_section,
    }

    return render_to_response('forms.html', templatePrarams, context_instance=RequestContext(request))


def addCompany(request):
    user = request.user

    user_groups = user.groups.values_list('name', flat=True)

    if not 'Company Creator' in user_groups:
        return func.permissionDenied()

    form = None

    branches = Branch.objects.all()
    branches_ids = [branch.pk for branch in branches]
    branches = Item.getItemsAttributesValues(("NAME",), branches_ids)

    countries = func.getItemsList("Country", 'NAME')
    tpp = func.getItemsList("Tpp", 'NAME')

    pages = None

    choosen_country = 0
    choosen_tpp = 0
    currentBranch = 0


    if request.POST:

        currentBranch = int(request.POST.get('BRANCH', 0))

        try:
            choosen_tpp = int(request.POST.get('TPP', 0))
        except ValueError:
            choosen_tpp = 0


        values = {}
        values.update(request.POST)
        values.update({'POSITION': request.POST.get('Lat', '') + ',' + request.POST.get('Lng')})
        values.update(request.FILES)
        branch = request.POST.get('BRANCH', "")
        choosen_country = request.POST.get('COUNTRY', "")

        form = ItemForm('Company', values=values)
        form.clean()
        try:
            choosen_country = int(choosen_country)
        except ValueError:
            form.errors.update({"COUNTRY": _("Please select a country")})


        if choosen_country not in countries:
            form.errors.update({"COUNTRY": _("Invalid Country")})



        Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=5, fields=("content", 'title'))
        pages = Page(request.POST, request.FILES, prefix="pages")
        if getattr(pages, 'new_objects', False):
            pages = pages.new_objects
        else:
            pages = ""


        if form.is_valid():

            func.notify("item_creating", 'notification', user=request.user)

            addNewCompany.delay(request.POST, request.FILES, user, settings.SITE_ID,
                                branch=branch, lang_code=trans_real.get_language())

            return HttpResponseRedirect(reverse('companies:main'))

    template = loader.get_template('Companies/addForm.html')

    context = RequestContext(request, {'form': form, 'branches': branches, 'countries': countries, 'tpp': tpp, 'pages': pages,
                                       'choosen_tpp': choosen_tpp, 'choosen_country': choosen_country, 'currentBranch': currentBranch })

    newsPage = template.render(context)

    return newsPage


def updateCompany(request, item_id):


    item = Organization.objects.get(pk=item_id)

    perm_list = item.getItemInstPermList(request.user)

    if 'change_company' not in perm_list:
        return func.permissionDenied()
    try:
        choosen_country = Country.objects.get(p2c__child=item_id).pk
    except ObjectDoesNotExist:
        choosen_country = ""
    try:
        choosen_tpp = Tpp.objects.get(p2c__child=item_id).pk
    except ObjectDoesNotExist:
        choosen_tpp = ""

    countries = func.getItemsList("Country", 'NAME')
    tpp = func.getItemsList("Tpp", 'NAME')

    company = Company.objects.get(pk=item_id)

    Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
    pages = Page(request.POST, request.FILES, prefix="pages", parent_id=item_id)
    if getattr(pages, 'new_objects', False):
        pages = pages.new_objects
    else:
        pages = pages.queryset

    branches = {}
    currentBranch = ''
    form = None

    if request.method != 'POST':
        branches = Branch.objects.all()
        branches_ids = [branch.pk for branch in branches]
        branches = Item.getItemsAttributesValues(("NAME",), branches_ids)

        try:
            currentBranch = Branch.objects.get(p2c__child=item_id).pk
        except ObjectDoesNotExist:
            pass

        form = ItemForm('Company', id=item_id)

    if request.POST:
        user = request.user

        values = {}
        values.update(request.POST)
        values.update({'POSITION': request.POST.get('Lat', '') + ',' + request.POST.get('Lng')})
        values.update(request.FILES)
        branch = request.POST.get('BRANCH', "")
        country = request.POST.get('COUNTRY', "")

        form = ItemForm('Company', values=values, id=item_id)
        form.clean()

        try:
            country = int(country)
        except ValueError:
            form.errors.update({"COUNTRY": _("Please select a country")})


        if country not in countries:
            form.errors.update({"COUNTRY": _("Invalid Country")})



        if form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addNewCompany.delay(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id, branch=branch, lang_code=trans_real.get_language())

            return HttpResponseRedirect(request.GET.get('next'), reverse('companies:main'))


    template = loader.get_template('Companies/addForm.html')

    templateParams = {
        'form': form,
        'branches': branches,
        'currentBranch': currentBranch,
        'company': company,
        'choosen_country': choosen_country,
        'countries': countries,
        'choosen_tpp': choosen_tpp,
        'tpp': tpp,
        'pages': pages
    }

    context = RequestContext(request, templateParams)
    newsPage = template.render(context)

    return newsPage



def deleteCompany(request, item_id):
    item = Organization.objects.get(pk=item_id)

    perm_list = item.getItemInstPermList(request.user)

    if 'delete_company' not in perm_list:
        return func.permissionDenied()

    instance = Company.objects.get(pk=item_id)
    instance.activation(eDate=now())
    instance.end_date = now()
    instance.reindexItem()

    return HttpResponseRedirect(request.GET.get('next'), reverse('companies:main'))

def _tabsGallery(request, item, page=1):

    item = get_object_or_404(Company, pk=item)
    file = request.FILES.get('Filedata', None)

    permissionsList = item.getItemInstPermList(request.user)

    has_perm = False

    if 'change_company' in permissionsList:
        has_perm = True


    if file is not None:


        if has_perm:

            try:
                file = add(request.FILES['Filedata'], {'big': {'box': (130, 120), 'fit': True}})
                instance = Gallery(photo=file, create_user=request.user)
                instance.save()

                Relationship.setRelRelationship(parent=item, child=instance, user=request.user, type='dependence')

                return HttpResponse('')
            except Exhibition:
                return HttpResponseBadRequest()
        else:
            return HttpResponseBadRequest()
    else:
        photos = Gallery.objects.filter(c2p__parent=item).all()

        paginator = Paginator(photos, 10)

        try:
            onPage = paginator.page(page)
        except Exception:
            onPage = paginator.page(1)

        url_paginator = "companies:tabs_gallery_paged"
        paginator_range = func.getPaginatorRange(onPage)

        templateParams = {
            'page': onPage,
            'paginator_range': paginator_range,
            'url_paginator': url_paginator,
            'gallery': onPage.object_list,
            'has_perm': has_perm,
            'item_id': item.pk,
            'pageNum': page,
            'url_parameter': item.pk
        }


        return render_to_response('Companies/tabGallery.html', templateParams, context_instance=RequestContext(request))


def galleryStructure(request, item, page=1):

    item = get_object_or_404(Company, pk=item)

    file = request.FILES.get('Filedata', None)

    permissionsList = item.getItemInstPermList(request.user)

    has_perm = False

    if 'change_company' in permissionsList:
        has_perm = True

    photos = Gallery.objects.filter(c2p__parent=item).all()

    paginator = Paginator(photos, 10)

    try:
        onPage = paginator.page(page)
    except Exception:
        onPage = paginator.page(1)

    url_paginator = "companies:tabs_gallery_paged"
    paginator_range = func.getPaginatorRange(onPage)

    templateParams = {
        'page': onPage,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'gallery': onPage.object_list,
        'pageNum': page,
        'url_parameter': item.pk,
        'has_perm': has_perm
    }

    return render_to_response('Companies/tab_gallery_structure.html', templateParams, context_instance=RequestContext(request))

def galleryRemoveItem(request, item):
    photo = get_object_or_404(Gallery, pk=item)

    comp = Company.objects.get(p2c__child=photo)

    permissionsList = comp.getItemInstPermList(request.user)


    if 'change_company' in permissionsList:
        photo.delete()

    return HttpResponse()


def sendMessage(request):
    response = ""
    if request.is_ajax():
        if request.user.is_authenticated() and request.POST.get('company', False):
            if request.POST.get('message', False) or request.FILES.get('file', False):
                company_pk = request.POST.get('company')

                #this condition as temporary design for separation Users and Organizations
                if Cabinet.objects.filter(pk=int(company_pk)).exists():
                    addMessages(request, text=request.POST.get('message', ""), recipient=int(company_pk))
                    response = _('You have successfully sent the message.')
                # /temporary condition for separation Users and Companies

                else:
                    email = Company.objects.get(pk=int(company_pk)).getAttributeValues('EMAIL')
                    if len(email) == 0:
                        email = 'admin@tppcenter.com'
                        subject = _('This message was sent to company with id:') + company_pk
                    else:
                        email = email[0]
                        subject = _('New message')
                    mail = EmailMessage(subject, request.POST.get('message', ""), 'noreply@tppcenter.com', [email])
                    attachment = request.FILES.get('file', False)
                    if attachment:
                       mail.attach(attachment.name, attachment.read(), attachment.content_type)
                    mail.send()
                    response = _('You have successfully sent the message.')

            else:
                response = _('Message or file are required')
        else:
             response = _('Only registered users can send the messages')

        return HttpResponse(response)
