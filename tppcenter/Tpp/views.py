import json
import logging
from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator
from django.forms.models import modelformset_factory
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _
from django.conf import settings
from django.utils.translation import trans_real
from haystack.backends import SQ

from appl import func
from appl.models import Tpp, Country, Organization, Company, Tender, News, Exhibition, BusinessProposal, Department, \
                        Cabinet, InnovationProject, Vacancy, Gallery, AdditionalPages
from core.models import Item, Relationship, Group, User
from tppcenter.cbv import ItemDetail, ItemsList
from tppcenter.forms import ItemForm, BasePages
from core.tasks import addNewTpp
from core.amazonMethods import add


logger = logging.getLogger('django.request')

class get_tpp_list(ItemsList):

    #pagination url
    url_paginator = "tpp:paginator"
    url_my_paginator = "tpp:my_main_paginator"

    #Lists of required scripts and styles for ajax request
    styles = [
        settings.STATIC_URL + 'tppcenter/css/news.css',
        settings.STATIC_URL + 'tppcenter/css/company.css',
        settings.STATIC_URL + 'tppcenter/css/tpp.reset.css'
    ]

    current_section = _("Tpp")

    #allowed filter list
    filterList = ['country']

    def dispatch(self, request, *args, **kwargs):

        if request.user.is_authenticated():

            user_groups = request.user.groups.values_list('name', flat=True)

            if request.user.is_manager and 'TPP Creator' in user_groups:
                self.addUrl = 'tpp:add'

        return super().dispatch(request, *args, **kwargs)


    model = Tpp

    def ajax(self, request, *args, **kwargs):
        self.template_name = 'Tpp/contentPage.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'Tpp/index.html'

    def _get_my(self):
        current_organization = self.request.session.get('current_company', False)

        if current_organization is False:
            if self.request.is_ajax():
                self.template_name = 'permissionDen.html'
            else:
                self.template_name = 'main/denied.html'

            return SQ(django_id=0)

        return SQ(django_id=current_organization) | SQ(company=current_organization)


class get_tpp_detail(ItemDetail):

    model = Tpp
    template_name = 'Tpp/detailContent.html'

    current_section = _("Tpp")

    def get_context_data(self, **kwargs):
        context = super(get_tpp_detail, self).get_context_data(**kwargs)

        context.update({
            'photos': self._get_gallery(),
            'additionalPages': self._get_additional_pages(),
        })

        return context


@login_required(login_url='/login/')
def tppForm(request, action, item_id=None):
    if item_id:
       if not Tpp.active.get_active().filter(pk=item_id).exists():
         return HttpResponseNotFound()


    current_section = _("Tpp")

    if action == 'add':
        tppPage = addTpp(request)
    else:
        tppPage = updateTpp(request, item_id)

    if isinstance(tppPage, HttpResponseRedirect) or isinstance(tppPage, HttpResponse):
        return tppPage

    templateParams = {
        'formContent': tppPage,
        'current_section': current_section
    }

    return render_to_response('forms.html', templateParams, context_instance=RequestContext(request))


def addTpp(request):

    form = None
    countries = func.getItemsList("Country", 'NAME')
    user = request.user

    pages = None

    user_groups = user.groups.values_list('name', flat=True)

    if not user.is_manager or not 'TPP Creator' in user_groups:
        return func.permissionDenied()

    if request.POST:
        user = request.user

        values = {}
        values.update(request.POST)
        values.update({'POSITION': request.POST.get('Lat', '') + ',' + request.POST.get('Lng')})
        values.update(request.FILES)

        Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=5, fields=("content", 'title'))
        pages = Page(request.POST, request.FILES, prefix="pages")
        if getattr(pages, 'new_objects', False):
            pages = pages.new_objects
        else:
            pages = ""

        form = ItemForm('Tpp', values=values)
        form.clean()

        if form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addNewTpp.delay(request.POST, request.FILES, user, settings.SITE_ID, lang_code=trans_real.get_language())

            return HttpResponseRedirect(reverse('tpp:main'))

    template = loader.get_template('Tpp/addForm.html')
    context = RequestContext(request, {'form': form, 'countries': countries, 'pages': pages})
    tppPage = template.render(context)

    return tppPage


def updateTpp(request, item_id):

    item = Organization.objects.get(pk=item_id)

    perm_list = item.getItemInstPermList(request.user)

    if 'change_tpp' not in perm_list:
        return func.permissionDenied()

    try:
        choosen_country = Country.objects.get(p2c__child=item_id)
    except ObjectDoesNotExist:
        choosen_country = ""


    countries = func.getItemsList("Country", 'NAME')
    tpp = Tpp.objects.get(pk=item_id)

    form = ItemForm('Tpp', id=item_id)

    Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
    pages = Page(request.POST, request.FILES, prefix="pages", parent_id=item_id)
    if getattr(pages, 'new_objects', False):
        pages = pages.new_objects
    else:
        pages = pages.queryset





    if request.POST:
        user = request.user


        values = {}
        values.update(request.POST)
        values.update({'POSITION': request.POST.get('Lat', '') + ',' + request.POST.get('Lng')})
        values.update(request.FILES)

        form = ItemForm('Tpp', values=values, id=item_id)
        form.clean()

        if form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addNewTpp.delay(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id,
                            lang_code=trans_real.get_language())

            return HttpResponseRedirect(request.GET.get('next', reverse('tpp:main')))

    template = loader.get_template('Tpp/addForm.html')

    templateParams = {
        'form': form,
        'choosen_country': choosen_country,
        'countries': countries,
        'tpp': tpp,
        'pages': pages
    }

    context = RequestContext(request, templateParams)
    tppPage = template.render(context)

    return tppPage

def _tabsCompanies(request, tpp, page=1):

        companies = func.getActiveSQS().models(Company).filter(tpp=tpp)
        attr = ('NAME', 'IMAGE', 'SITE_NAME', 'TELEPHONE_NUMBER', 'SLUG')

        result = func.setPaginationForSearchWithValues(companies, *attr, page_num=10, page=page)


        companyList = result[0]

        page = result[1]
        paginator_range = func.getPaginatorRange(page)

        url_paginator = "tpp:tab_companies_paged"

        templateParams = {
            'companyList': companyList,
            'page': page,
            'paginator_range': paginator_range,
            'url_paginator': url_paginator,
            'url_parameter': tpp
        }


        return render_to_response('Tpp/tabCompanies.html', templateParams, context_instance=RequestContext(request))

def _tabsNews(request, tpp, page=1):

        news = func.getActiveSQS().models(News).filter(company=0, tpp=tpp)
        attr = ('NAME', 'IMAGE', 'DETAIL_TEXT', 'SLUG')

        result = func.setPaginationForSearchWithValues(news, *attr, page_num=5, page=page)


        newsList = result[0]

        page = result[1]
        paginator_range = func.getPaginatorRange(page)

        url_paginator = "tpp:tab_news_paged"

        templateParams = {
            'newsList': newsList,
            'page': page,
            'paginator_range': paginator_range,
            'url_paginator': url_paginator,
            'url_parameter': tpp
        }


        return render_to_response('Tpp/tabNews.html', templateParams, context_instance=RequestContext(request))


def _tabsTenders(request, tpp, page=1):

        tenders = func.getActiveSQS().models(Tender).filter(company=0, tpp=tpp)
        attr = ('NAME', 'START_EVENT_DATE', 'END_EVENT_DATE', 'COST', 'CURRENCY', 'SLUG')

        result = func.setPaginationForSearchWithValues(tenders, *attr, page_num=5, page=page)


        tendersList = result[0]

        page = result[1]
        paginator_range = func.getPaginatorRange(page)

        url_paginator = "tpp:tab_tenders_paged"

        templateParams = {
            'tendersList': tendersList,
            'page': page,
            'paginator_range': paginator_range,
            'url_paginator': url_paginator,
            'url_parameter': tpp
        }


        return render_to_response('Tpp/tabTenders.html', templateParams, context_instance=RequestContext(request))

def _tabsExhibitions(request, tpp, page=1):

        exhibition = func.getActiveSQS().models(Exhibition).filter(company=0, tpp=tpp)
        attr = ('NAME', 'SLUG', 'START_EVENT_DATE', 'END_EVENT_DATE', 'CITY')

        result = func.setPaginationForSearchWithValues(exhibition, *attr, page_num=5, page=page)


        exhibitionList = result[0]

        page = result[1]
        paginator_range = func.getPaginatorRange(page)

        url_paginator = "tpp:tab_exhibitions_paged"

        templateParams = {
            'exhibitionList': exhibitionList,
            'page': page,
            'paginator_range': paginator_range,
            'url_paginator': url_paginator,
            'url_parameter': tpp
        }



        return render_to_response('Tpp/tabExhibitions.html', templateParams, context_instance=RequestContext(request))


def _tabsProposals(request, tpp, page=1):

        products = func.getActiveSQS().models(BusinessProposal).filter(company=0, tpp=tpp)
        attr = ('NAME', 'SLUG')

        result = func.setPaginationForSearchWithValues(products, *attr, page_num=5, page=page)


        proposalList = result[0]

        page = result[1]
        paginator_range = func.getPaginatorRange(page)

        url_paginator = "tpp:tab_proposal_paged"

        templateParams = {
            'productsList': proposalList,
            'page': page,
            'paginator_range': paginator_range,
            'url_paginator': url_paginator,
            'url_parameter': tpp
        }


        return render_to_response('Companies/tabProposal.html', templateParams, context_instance=RequestContext(request))


def _tabsInnovs(request, tpp, page=1):

        products = func.getActiveSQS().models(InnovationProject).filter(company=0, tpp=tpp)
        attr = ('NAME', 'COST', 'CURRENCY', 'SLUG')

        result = func.setPaginationForSearchWithValues(products, *attr, page_num=5, page=page)


        innovList = result[0]

        page = result[1]
        paginator_range = func.getPaginatorRange(page)

        url_paginator = "tpp:tab_innov_paged"

        templateParams = {
            'productsList': innovList,
            'page': page,
            'paginator_range': paginator_range,
            'url_paginator': url_paginator,
            'url_parameter': tpp
        }


        return render_to_response('Companies/tabInnov.html', templateParams, context_instance=RequestContext(request))

def _tabsStructure(request, tpp, page=1):
    '''
        Show content of the TPP-Structure panel
    '''
    organization = get_object_or_404(Tpp, pk=tpp)
    permissionsList = organization.getItemInstPermList(request.user)

    if request.is_ajax() and request.user.is_authenticated():

        try:
            id = int(request.POST.get("id", 0))
        except ValueError:
            id = 0

        name = request.POST.get('name', '').strip()
        action = request.POST.get("action", None)

        if "change_tpp" not in permissionsList and action is not None: # Error
            return HttpResponseBadRequest()

        if action == "add" and len(name) > 0:

            if id == 0: # new department
                obj_dep = Department.objects.create(title=name, create_user=request.user)
                Relationship.setRelRelationship(organization, obj_dep, request.user, type='hierarchy')
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


    departments = func.getActiveSQS().models(Department).filter(tpp=tpp).order_by('text')

    paginator = Paginator(departments, 10)
    departments = paginator.page(page)
    paginator_range = func.getPaginatorRange(departments)
    url_paginator = "tpp:tab_structure_paged"
    departmentsDict = {}
    departmentsList = []

    for department in departments.object_list:
        department.vacancyList = []
        departmentsDict[int(department.pk)] = department
        departmentsList.append(department.pk)

    vacancies = func.getActiveSQS().models(Vacancy).filter(tpp=tpp, department__in=departmentsList).order_by('text')

    for vacancy in vacancies:
        departmentsDict[int(vacancy.department)].vacancyList.append(vacancy)


    templateParams = {
        'permissionsList': permissionsList,
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'url_parameter': tpp,
        'departments': departmentsDict,
        'item_pk': tpp
    }

    return render_to_response('Tpp/tabStructure.html', templateParams, context_instance=RequestContext(request))

def _tabsStaff(request, tpp, page=1):
    '''
        Show content of the TPP-Staff panel
    '''
    organization = get_object_or_404(Tpp, pk=tpp)
    permissionsList = organization.getItemInstPermList(request.user)

    if request.is_ajax() and request.user.is_authenticated():

        action = request.POST.get('action', False)

        action = action if action else request.GET.get('action', None)

        if "add_cabinet" not in permissionsList and action is not None: # Error
            return HttpResponseBadRequest()

        if action == "department":
            departments = [{'name': _("Select department"), "value": ""}]

            for department in func.getActiveSQS().models(Department).filter(tpp=tpp).order_by('text'):
                departments.append({"name": department.text, "value": department.pk})

            return HttpResponse(json.dumps(departments))

        elif action == "vacancy":

            department = int(request.GET.get("department", 0))

            if department <= 0:
                return HttpResponseBadRequest()

            vacancies = [{'name': _("Select vacancy"), "value": ""}]
            for vacancy in func.getActiveSQS().models(Vacancy).filter(tpp=tpp).order_by('text'):
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
                department = Department.objects.get(pk=department, c2p__parent=tpp)
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
            elif Cabinet.objects.filter(pk=cab.pk, c2p__parent__c2p__parent__c2p__parent=tpp).exists():
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

                vacancy = get_object_or_404(Vacancy, p2c__child=cabinet.pk, c2p__parent__c2p__parent=tpp)

                Relationship.objects.filter(parent__c2p__parent__c2p__parent=tpp, child=cabinet,
                                                type='relation').delete()

                cabinet.reindexItem()
                vacancy.reindexItem()

    cabinets = Cabinet.objects.filter(c2p__parent__c2p__parent__c2p__parent=tpp).distinct()
    attr = ('USER_FIRST_NAME', 'USER_MIDDLE_NAME', 'USER_LAST_NAME', 'EMAIL', 'IMAGE', 'SLUG')
    workersList, page = func.setPaginationForItemsWithValues(cabinets, *attr, page_num=10, page=page)

    dep_lst = tuple(Department.objects.filter(c2p__parent=tpp).values_list('pk', flat=True))
    org_lst = Item.getItemsAttributesValues(('NAME',), dep_lst)
    correlation = list(Department.objects.filter(c2p__parent=tpp).values_list('pk', 'p2c__child__p2c__child'))

    for cab_id, cab_att in workersList.items(): #get Cabinet instance
        if not cab_att:
            continue
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
    url_paginator = "tpp:tab_staff_paged"

    #create full list of TPP's Departments
    departments = func.getActiveSQS().models(Department).filter(tpp=tpp).order_by('text')

    dep_lst = [dep.pk for dep in departments]

    if len(dep_lst) == 0:
        departmentsList = []
    else:
        departmentsList = Item.getItemsAttributesValues(('NAME',), dep_lst)

    #create list of TPP's Vacancies
    vacancies = func.getActiveSQS().models(Vacancy).filter(tpp=tpp).order_by('text')

    vac_lst = [vac.pk for vac in vacancies]

    if len(vac_lst) == 0:
        vacanciesList = []
    else:
        vacanciesList = Item.getItemsAttributesValues(('NAME',), vac_lst)
        # correlation between Departments and Vacancies
        correlation = list(Department.objects.filter(c2p__parent=tpp).values_list('pk', 'p2c__child'))

        # add into Vacancy's attribute a new key 'DEPARTMENT_ID' with Department ID
        for vac_id, vac_att in vacanciesList.items(): #get Vacancy instance
            for t in correlation: #lookup into correlation list
                if t[1] == vac_id: #if Vacancy ID is equal then...
                    #... add a new key into Vacancy attribute dictionary
                    vac_att['DEPARTMENT_ID'] = [t[0]]
                    break

        correlation = list(Department.objects.filter(c2p__parent=tpp).values_list('p2c__child__p2c__child', 'p2c__child'))

        # add into worker's list attribute a new key 'VACANCY' with Vacancy ID
        for cab_id, cab_att in workersList.items(): #get Cabinet instance
            for t in correlation: #lookup into correlation list
                if t[0] == cab_id: #if Cabinet ID is equal then...
                    for vac_id, vac_attr in vacanciesList.items():
                        if t[1] == vac_id:
                            #... add a new key into User (Cabinet) attribute dictionary
                            cab_att['VACANCY'] = vac_attr['NAME']
                            break

    templateParams = {
        'workersList': workersList,
        'departmentsList': departmentsList, #list for adding user form
        'vacanciesList': vacanciesList,     #list for adding user form
        'permissionsList': permissionsList,
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'url_parameter': tpp,
        'item_pk': tpp
    }

    return render_to_response('Tpp/tabStaff.html', templateParams, context_instance=RequestContext(request))

def _tabsGallery(request, item, page=1):

    item = get_object_or_404(Tpp, pk=item)
    file = request.FILES.get('Filedata', None)

    permissionsList = item.getItemInstPermList(request.user)

    has_perm = False

    if 'change_tpp' in permissionsList:
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

        url_paginator = "tpp:tabs_gallery_paged"
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


        return render_to_response('Tpp/tabGallery.html', templateParams, context_instance=RequestContext(request))


def galleryStructure(request, item, page=1):

    item = get_object_or_404(Tpp, pk=item)
    photos = Gallery.objects.filter(c2p__parent=item).all()

    paginator = Paginator(photos, 10)

    try:
        onPage = paginator.page(page)
    except Exception:
        onPage = paginator.page(1)

    url_paginator = "tpp:tabs_gallery_paged"
    paginator_range = func.getPaginatorRange(onPage)

    templateParams = {
        'page': onPage,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'gallery': onPage.object_list,
        'pageNum': page,
        'url_parameter': item.pk
    }

    return render_to_response('Tpp/tab_gallery_structure.html', templateParams, context_instance=RequestContext(request))

def galleryRemoveItem(request, item):
    photo = get_object_or_404(Gallery, pk=item)

    tpp = Tpp.objects.get(p2c__child=photo)

    permissionsList = tpp.getItemInstPermList(request.user)


    if 'change_tpp' in permissionsList:
        photo.delete()

    return HttpResponse()
