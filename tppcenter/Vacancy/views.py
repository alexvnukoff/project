from django.db.models import Q
from django.utils.timezone import now
from appl import func
from appl.models import Tpp, Country, Organization, Company, Tender, News, Exhibition, BusinessProposal, Department, \
                        Cabinet, InnovationProject, Vacancy, Requirement, Resume
from core.models import Item, Relationship, Group, User
from core.tasks import addNewTpp, addNewRequirement
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _
from haystack.query import SQ, SearchQuerySet
from tppcenter.forms import ItemForm
import json
from core.tasks import addNewTpp
from django.conf import settings
from django.utils import timezone
from datetime import datetime
from django.core.cache import cache
from django.utils.translation import trans_real
import logging
logger = logging.getLogger('django.request')

def get_vacancy_list(request, page=1, item_id=None, my=None, slug=None):
    #   if slug and  not Value.objects.filter(item=item_id, attr__title='SLUG', title=slug).exists():
    #   slug = Value.objects.get(item=item_id, attr__title='SLUG').title
    #   return HttpResponseRedirect(reverse('tpp:detail',  args=[slug]))
    if item_id:
        if not Item.active.get_active().filter(pk=item_id).exists():
            return HttpResponseNotFound()

    description = ''
    title = ''
    resumesValues = ''

    if item_id is None:
        try:
            vacancyPage = _vacancyContent(request, page, my)
        except ObjectDoesNotExist:
            vacancyPage = func.emptyCompany()
    else:
        result = _vacancyDetailContent(request, item_id)
        if request.user.is_authenticated():
            resumes =  Resume.active.get_active().filter(c2p__parent=Cabinet.objects.get(user=request.user.pk))
            resumes_ids = [resume.pk for resume in resumes]
            resumesValues = Item.getItemsAttributesValues(('NAME',),resumes_ids)
        vacancyPage = result[0]
        description = result[1]
        title = result[2]



    scripts = []


    current_section = _("Vacancy")

    templateParams = {
        'current_section': current_section,
        'vacancyPage': vacancyPage,
        'scripts': scripts,
        'addNew': reverse('vacancy:add'),
        'item_id': item_id,
        'description': description,
        'title': title,
        'resumesValues': resumesValues
    }

    return render_to_response("Vacancy/index.html", templateParams, context_instance=RequestContext(request))



def _vacancyContent(request, page=1, my=None):

    #tpp = Tpp.active.get_active().order_by('-pk')
    cached = False
    cache_name = "vacancy_list_result_page_%s" % page

    q = request.GET.get('q', '')

    if not my and func.cachePisibility(request):
        cached = cache.get(cache_name)

    if not cached:

        if not my:
           vacancies = Requirement.active.get_active()
           url_paginator = "vacancy:paginator"
           params = {}

           # filters, searchFilter = func.filterLive(request)

          # sqs = func.getActiveSQS().models(Tpp)

            #if len(searchFilter) > 0:
             #   sqs = sqs.filter(searchFilter)

           # if q != '':
            #    sqs = sqs.filter(title=q)

            #sortFields = {
             #   'date': 'id',
             #   'name': 'title_sort'
            #}

            #order = []

            #sortField1 = request.GET.get('sortField1', 'date')
            #sortField2 = request.GET.get('sortField2', None)
            #order1 = request.GET.get('order1', 'desc')
            #order2 = request.GET.get('order2', None)

            #if sortField1 and sortField1 in sortFields:
            #   if order1 == 'desc':
            #        order.append('-' + sortFields[sortField1])
            #   else:
            #        order.append(sortFields[sortField1])
            #else:
            #    order.append('-id')

            # if sortField2 and sortField2 in sortFields:
            #    if order2 == 'desc':
            #       order.append('-' + sortFields[sortField2])
            #   else:
            #       order.append(sortFields[sortField2])


            #tpp = sqs.order_by(*order)


            #params = {
             #   'filters': filters,
              #  'sortField1': sortField1,
               # 'sortField2': sortField2,
                #'order1': order1,
                #'order2': order2
            #}
        else:
            current_organization = request.session.get('current_company', False)


            #read all Organizations which hasn't foreign key from Department and current User is create user or worker
            vacancies = Requirement.active.get_active().filter(c2p__parent__c2p__parent__c2p__parent=current_organization)

            url_paginator = "vacancy:my_main_paginator"
            params = {}


        attr = ('NAME', 'DETAIL_TEXT', 'CITY' ,'SLUG')


        result = func.setPaginationForItemsWithValues(vacancies, *attr,  page_num=5, page=page)

        vacancyList = result[0]
        vacancy_ids = [id for id in vacancyList.keys()]

        if request.user.is_authenticated():
            items_perms = func.getUserPermsForObjectsList(request.user, vacancy_ids, Requirement.__name__)
        else:
            items_perms = ""

        countries = Country.objects.filter(p2c__child__p2c__child__p2c__child__p2c__child__in=vacancy_ids).distinct().values('pk', 'p2c__child__p2c__child__p2c__child__p2c__child')
        countries_id = [country['pk'] for country in countries]
        countriesList = Item.getItemsAttributesValues(("NAME", 'FLAG', 'COUNTRY_FLAG'), countries_id)
        country_dict = {}

        for country in countries:
            country_dict[country['p2c__child__p2c__child__p2c__child__p2c__child']] = country['pk']

        for id, vacancy in vacancyList.items():
            toUpdate = {'COUNTRY_NAME': countriesList[country_dict[id]].get('NAME', [0]) if country_dict.get(id, 0) else [0],
                        'COUNTRY_FLAG': countriesList[country_dict[id]].get('FLAG', [0]) if country_dict.get(id, 0) else [0],
                        'FLAG_CLASS': countriesList[country_dict[id]].get('COUNTRY_FLAG', [0]) if country_dict.get(id, 0) else [0],
                        'COUNTRY_ID':  country_dict.get(id, 0)}
            vacancy.update(toUpdate)


        page = result[1]
        paginator_range = func.getPaginatorRange(page)


        template = loader.get_template('Vacancy/contentPage.html')

        templateParams = {
            'vacancyList': vacancyList,
            'page': page,
            'paginator_range': paginator_range,
            'url_paginator': url_paginator,
            'items_perms': items_perms,
            'current_path': request.get_full_path()
        }

        templateParams.update(params)


        context = RequestContext(request, templateParams)
        rendered = template.render(context)

        if not my and func.cachePisibility(request):
            cache.set(cache_name, rendered)

    else:
        rendered = cache.get(cache_name)

    return rendered


def _vacancyDetailContent(request, item_id):

    cache_name = "detail_%s" % item_id
    description_cache_name = "description_%s" % item_id
    cached = cache.get(cache_name)
    if not cached:

        requirement = get_object_or_404(Requirement, pk=item_id)
        requirementValues = requirement.getAttributeValues(*('NAME', 'DETAIL_TEXT', 'CITY', 'TYPE_OF_EMPLOYMENT', 'REQUIREMENTS', 'TERMS',
                                                     'IS_ANONYMOUS_VACANCY'))
        description = requirementValues.get('DETAIL_TEXT', False)[0] if requirementValues.get('DETAIL_TEXT', False) else ""
        description = func.cleanFromHtml(description)
        title = requirementValues.get('NAME', False)[0] if requirementValues.get('NAME', False) else ""


        organizatation = Organization.objects.get(p2c__child__p2c__child__p2c__child_id=item_id)

        organizationValues = organizatation.getAttributeValues('NAME', 'SLUG')


        template = loader.get_template('Vacancy/detailContent.html')
        context = RequestContext(request, {'requirementValues': requirementValues, 'organizationValues': organizationValues})
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
def vacancyForm(request, action, item_id=None):
    if item_id:
       if not Requirement.active.get_active().filter(pk=item_id).exists():
         return HttpResponseNotFound()


    current_section = _("Vacancy")

    if action == 'add':
        vacancyPage = addVacancy(request)
    elif action == 'update':
        vacancyPage = updateVacancy(request, item_id)
    elif action == 'delete':
        vacancyPage = deleteVacancy(request, item_id)


    if isinstance(vacancyPage, HttpResponseRedirect) or isinstance(vacancyPage, HttpResponse):
        return vacancyPage

    templateParams = {
        'formContent': vacancyPage,
        'current_section': current_section
    }

    return render_to_response('forms.html', templateParams, context_instance=RequestContext(request))

def addVacancy(request):

    form = None

    current_company = request.session.get('current_company', False)

    if not request.session.get('current_company', False):
         return func.emptyCompany()

    item = Organization.objects.get(pk=current_company)

    perm_list = item.getItemInstPermList(request.user)

    if 'add_requirement' not in perm_list:
         return func.permissionDenied()
    user = request.user

    result = getDepartamentsAndVacancies(current_company)
    departmentsList = result[0]
    vacanciesList = result[1]
    vacancy_error = ""






    if request.POST:
        user = request.user

        values = {}
        values.update(request.POST)

        values.update(request.FILES)

        form = ItemForm('Requirement', values=values)
        form.clean()

        if form.is_valid() and request.POST.get('VACANCY', False):
            func.notify("item_creating", 'notification', user=request.user)
            addNewRequirement(request.POST, request.FILES, user, settings.SITE_ID, lang_code=settings.LANGUAGE_CODE)

            return HttpResponseRedirect(reverse('vacancy:main'))
        if not request.POST.get('VACANCY', False):
            vacancy_error = _('You have to choose vacancy')

    template = loader.get_template('Vacancy/addForm.html')
    context = RequestContext(request, {'form': form, 'departmentsList': departmentsList, 'vacanciesList': vacanciesList, 'vacancy_error': vacancy_error })
    vacancyPage = template.render(context)

    return vacancyPage


def updateVacancy(request, item_id):

    item = Organization.objects.get(p2c__child__p2c__child__p2c__child_id=item_id)

    perm_list = item.getItemInstPermList(request.user)

    if 'change_requirement' not in perm_list:
        return func.permissionDenied()



    requirement = Requirement.objects.get(pk=item_id)
    vacancy_selected = Vacancy.objects.get(p2c__child=requirement).pk

    current_company = request.session.get('current_company', False)
    result = getDepartamentsAndVacancies(current_company)
    departmentsList = result[0]
    vacanciesList = result[1]
    vacancy_error = ""


    form = ItemForm('Requirement', id=item_id)




    if request.POST:
        user = request.user


        values = {}
        values.update(request.POST)

        values.update(request.FILES)

        form = ItemForm('Requirement', values=values, id=item_id)
        form.clean()

        if form.is_valid() and request.POST.get('VACANCY', False):
            func.notify("item_creating", 'notification', user=request.user)
            addNewRequirement(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id,
                            lang_code=settings.LANGUAGE_CODE)
            return HttpResponseRedirect(request.GET.get('next', reverse('vacancy:main')))
        if not request.POST.get('VACANCY', False):
            vacancy_error = _('You have to choose vacancy')



    template = loader.get_template('Vacancy/addForm.html')

    templateParams = {
        'form': form,
        'vacancy_error': vacancy_error,
        'vacancy_selected': vacancy_selected,
        'departmentsList': departmentsList,
        'vacanciesList': vacanciesList

    }

    context = RequestContext(request, templateParams)
    tppPage = template.render(context)

    return tppPage



def getDepartamentsAndVacancies(company):
    departments = func.getActiveSQS().models(Department).filter(company=company).order_by('text')

    dep_lst = [dep.id for dep in departments]

    if len(dep_lst) == 0:
        departmentsList = []
    else:
        departmentsList = Item.getItemsAttributesValues(('NAME',), dep_lst)

    #create list of Company's Vacancies
    vacancies = func.getActiveSQS().models(Vacancy).filter(company=company).order_by('text')

    vac_lst = [vac.id for vac in vacancies]

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


    return departmentsList, vacanciesList


def deleteVacancy(request, item_id):
    item = Organization.objects.get(p2c__child__p2c__child__p2c__child_id=item_id)

    perm_list = item.getItemInstPermList(request.user)

    if 'delete_requirement' not in perm_list:
        return func.permissionDenied()

    instance = Requirement.objects.get(pk=item_id)
    instance.activation(eDate=now())
    instance.end_date = now()


    return HttpResponseRedirect(request.GET.get('next'), reverse('vacancy:main'))


def sendResume(request):
    response = ""
    if request.is_ajax():
        if request.user.is_authenticated() and request.POST.get('VACANCY', False):
            if request.POST.get('RESUME', False):
                requirement = request.POST.get('VACANCY', "")
                resume = request.POST.get('RESUME', '')
                if Relationship.objects.filter(parent=Requirement.objects.get(pk=int(requirement)), child=Resume.objects.get(pk=int(resume))).exists():
                      response = _('You cannot send more than one resume at the same job position.')
                else:
                    Relationship.setRelRelationship(parent=Requirement.objects.get(pk=int(requirement)), child=Resume.objects.get(pk=int(resume)), user=request.user)
                    response = _('You have successfully sent the resume.')

            else:
                response = _('Resume  are required')
        else:
             response = _('Only registred users can send resume')

        return HttpResponse(response)