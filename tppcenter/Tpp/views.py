from django.db.models import Q
from appl import func
from appl.models import Tpp, Country, Organization, Company, Tender, News, Exhibition, BusinessProposal, Department, \
                        Cabinet, InnovationProject, Vacancy
from core.models import Item, Relationship, Group, User
from core.tasks import addNewTpp
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

def get_tpp_list(request, page=1, item_id=None, my=None, slug=None):
    #   if slug and  not Value.objects.filter(item=item_id, attr__title='SLUG', title=slug).exists():
    #   slug = Value.objects.get(item=item_id, attr__title='SLUG').title
    #   return HttpResponseRedirect(reverse('tpp:detail',  args=[slug]))
    if item_id:
        if not Item.active.get_active().filter(pk=item_id).exists():
            return HttpResponseNotFound()

    description = ''
    title = ''

    if item_id is None:
        try:
            tppPage = _tppContent(request, page, my)
        except ObjectDoesNotExist:
            tppPage = func.emptyCompany()
    else:
        result = _tppDetailContent(request, item_id)
        tppPage = result[0]
        description = result[1]
        title = result[2]

    styles = [
        settings.STATIC_URL + 'tppcenter/css/news.css',
        settings.STATIC_URL + 'tppcenter/css/company.css',
        settings.STATIC_URL + 'tppcenter/css/tpp.reset.css'
    ]

    scripts = []

    if not request.is_ajax():

        current_section = _("Tpp")

        templateParams = {
            'current_section': current_section,
            'tppPage': tppPage,
            'scripts': scripts,
            'styles': styles,
            'addNew': reverse('tpp:add'),
            'item_id': item_id,
            'description': description,
            'title': title
        }

        return render_to_response("Tpp/index.html", templateParams, context_instance=RequestContext(request))
    else:

        serialize = {
            'styles': styles,
            'scripts': scripts,
            'content': tppPage,
        }

        return HttpResponse(json.dumps(serialize))


def _tppContent(request, page=1, my=None):

    #tpp = Tpp.active.get_active().order_by('-pk')
    cached = False
    cache_name = "tpp_list_result_page_%s" % page

    q = request.GET.get('q', '')

    if not my and func.cachePisibility(request):
        cached = cache.get(cache_name)

    if not cached:

        if not my:
            filters, searchFilter = func.filterLive(request)

            sqs = func.getActiveSQS().models(Tpp)

            if len(searchFilter) > 0:
                sqs = sqs.filter(searchFilter)

            if q != '':
                sqs = sqs.filter(title=q)

            sortFields = {
                'date': 'id',
                'name': 'title_sort'
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


            tpp = sqs.order_by(*order)
            url_paginator = "tpp:paginator"

            params = {
                'filters': filters,
                'sortField1': sortField1,
                'sortField2': sortField2,
                'order1': order1,
                'order2': order2
            }
        else:
            current_organization = request.session.get('current_company', False)

            cab = Cabinet.objects.get(user=request.user)
            #read all Organizations which hasn't foreign key from Department and current User is create user or worker
            tpp = Tpp.active.get_active().filter(Q(create_user=request.user) |
                                                    Q(p2c__child__p2c__child__p2c__child=cab.pk)).distinct()

            url_paginator = "tpp:my_main_paginator"
            params = {}


        attr = ('NAME', 'IMAGE', 'ADDRESS', 'SITE_NAME', 'TELEPHONE_NUMBER', 'FAX', 'INN', 'DETAIL_TEXT', 'FLAG', 'SLUG')

        if not my:
             result = func.setPaginationForSearchWithValues(tpp, *attr,  page_num=5, page=page)
        else:
            result = func.setPaginationForItemsWithValues(tpp, *attr,  page_num=5, page=page)

        tppList = result[0]
        tpp_ids = [id for id in tppList.keys()]

        if request.user.is_authenticated():
            items_perms = func.getUserPermsForObjectsList(request.user, tpp_ids, Tpp.__name__)
        else:
            items_perms = ""

        countries = Country.objects.filter(p2c__child__in=tpp_ids).values('p2c__child', 'pk')
        countries_id = [country['pk'] for country in countries]
        countriesList = Item.getItemsAttributesValues(("NAME", 'FLAG', 'COUNTRY_FLAG'), countries_id)
        country_dict = {}

        for country in countries:
            country_dict[country['p2c__child']] = country['pk']

        for id, tpp in tppList.items():
            toUpdate = {'COUNTRY_NAME': countriesList[country_dict[id]].get('NAME', [0]) if country_dict.get(id, 0) else [0],
                        'COUNTRY_FLAG': countriesList[country_dict[id]].get('FLAG', [0]) if country_dict.get(id, 0) else [0],
                        'FLAG_CLASS': countriesList[country_dict[id]].get('COUNTRY_FLAG', [0]) if country_dict.get(id, 0) else [0],
                        'COUNTRY_ID':  country_dict.get(id, 0)}
            tpp.update(toUpdate)


        page = result[1]
        paginator_range = func.getPaginatorRange(page)


        template = loader.get_template('Tpp/contentPage.html')

        templateParams = {
            'tppList': tppList,
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


def _tppDetailContent(request, item_id):

    cache_name = "detail_%s" % item_id
    description_cache_name = "description_%s" % item_id
    cached = cache.get(cache_name)
    if not cached:

        tpp = get_object_or_404(Tpp, pk=item_id)
        tppValues = tpp.getAttributeValues(*('NAME', 'DETAIL_TEXT', 'FLAG', 'IMAGE', 'POSITION', 'ADDRESS',
                                                     'TELEPHONE_NUMBER', 'FAX', 'EMAIL', 'SITE_NAME', 'ANONS'))
        description = tppValues.get('DETAIL_TEXT', False)[0] if tppValues.get('DETAIL_TEXT', False) else ""
        description = func.cleanFromHtml(description)
        title = tppValues.get('NAME', False)[0] if tppValues.get('NAME', False) else ""


        if not tppValues.get('FLAG', False):
           try:
               country = Country.objects.get(p2c__child=tpp, p2c__type='dependence').getAttributeValues(*('FLAG', 'NAME','COUNTRY_FLAG'))
           except:
               country = ""
        else:
           country = ""

        template = loader.get_template('Tpp/detailContent.html')
        context = RequestContext(request, {'tppValues': tppValues, 'country': country, 'item_id': item_id})
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

    user_groups = user.groups.values_list('name', flat=True)

    if not user.is_manager or not 'Tpp Creator' in user_groups:
        return func.permissionDenied()

    if request.POST:
        user = request.user

        values = {}
        values.update(request.POST)
        values.update({'POSITION': request.POST.get('Lat', '') + ',' + request.POST.get('Lng')})
        values.update(request.FILES)

        form = ItemForm('Tpp', values=values)
        form.clean()

        if form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addNewTpp.delay(request.POST, request.FILES, user, settings.SITE_ID, lang_code=settings.LANGUAGE_CODE)

            return HttpResponseRedirect(reverse('tpp:main'))

    template = loader.get_template('Tpp/addForm.html')
    context = RequestContext(request, {'form': form, 'countries': countries})
    tppPage = template.render(context)

    return tppPage


def updateTpp(request, item_id):

    item = Organization.objects.get(pk=item_id)

    perm_list = item.getItemInstPermList(request.user)

    if 'change_tpp' not in perm_list:
        return func.permissionDenied()

    try:
        choosen_country = Country.objects.get(p2c__child__id=item_id)
    except ObjectDoesNotExist:
        choosen_country = ""


    countries = func.getItemsList("Country", 'NAME')
    tpp = Tpp.objects.get(pk=item_id)

    form = ItemForm('Tpp', id=item_id)




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
                            lang_code=settings.LANGUAGE_CODE)

            return HttpResponseRedirect(request.GET.get('next', reverse('tpp:main')))

    template = loader.get_template('Tpp/addForm.html')

    templateParams = {
        'form': form,
        'choosen_country': choosen_country,
        'countries': countries,
        'tpp': tpp
    }

    context = RequestContext(request, templateParams)
    tppPage = template.render(context)

    return tppPage

def _tabsCompanies(request, tpp, page=1):
    cache_name = "Companies_tab_tpp_%s_page_%s" % (tpp, page)
    cached = cache.get(cache_name)

    if not cached:
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
        cache.set(cache_name, templateParams, 60*60)
    else:
        templateParams = cached

    return render_to_response('Tpp/tabCompanies.html', templateParams, context_instance=RequestContext(request))

def _tabsNews(request, tpp, page=1):
    cache_name = "News_tab_tpp_%s_page_%s" % (tpp, page)
    cached = cache.get(cache_name)

    if not cached:
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
        cache.set(cache_name, templateParams, 60*60)
    else:
        templateParams = cached

    return render_to_response('Tpp/tabNews.html', templateParams, context_instance=RequestContext(request))


def _tabsTenders(request, tpp, page=1):
    cache_name = "Tenders_tab_tpp_%s_page_%s" % (tpp, page)
    cached = cache.get(cache_name)

    if not cached:
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
        cache.set(cache_name, templateParams, 60*60)
    else:
        templateParams = cached

    return render_to_response('Tpp/tabTenders.html', templateParams, context_instance=RequestContext(request))

def _tabsExhibitions(request, tpp, page=1):
    cache_name = "Exhibitions_tab_tpp_%s_page_%s" % (tpp, page)
    cached = cache.get(cache_name)

    if not cached:
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
        cache.set(cache_name, templateParams, 60*60)
    else:
        templateParams = cached   


    return render_to_response('Tpp/tabExhibitions.html', templateParams, context_instance=RequestContext(request))


def _tabsProposals(request, tpp, page=1):
    cache_name = "Proposal_tab_tpp_%s_page_%s" % (tpp, page)
    cached = cache.get(cache_name)

    if not cached:
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
        cache.set(cache_name, templateParams, 60*60)
    else:
        templateParams = cached

    return render_to_response('Companies/tabProposal.html', templateParams, context_instance=RequestContext(request))


def _tabsInnovs(request, tpp, page=1):
    cache_name = "Innov_tab_tpp_%s_page_%s" % (tpp, page)
    cached = cache.get(cache_name)

    if not cached:
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
        cache.set(cache_name, templateParams, 60*60)
    else:
        templateParams = cached

    return render_to_response('Companies/tabInnov.html', templateParams, context_instance=RequestContext(request))

def _tabsStructure(request, tpp, page=1):
    '''
        Show content of the Company-details-structure panel
    '''
    #check if there Department for deletion
    comp = Tpp.objects.get(pk=tpp)
    departmentForDeletion = request.POST.get('departmentID', 0)

    try:
        departmentForDeletion = int(departmentForDeletion)
    except ValueError:
        departmentForDeletion = 0

    if departmentForDeletion > 0:
        dep_lst = Department.objects.filter(pk=departmentForDeletion)
        for d in dep_lst:
            try:
                d.delete()
            except Exception as e:
                print('Can not delete Department. The reason is: ' + str(e))
                pass

    #check if there Department for adding
    departmentToChange = request.POST.get('departmentName', '')

    if len(departmentToChange):
        usr = request.user
        #if update department we receive previous name
        prevDepName = request.POST.get('prevDepName', '')
        try:
            #check is there department with 'old' name
            obj_dep = Department.objects.get(c2p__parent=tpp, item2value__attr__title="NAME", item2value__title=prevDepName)
        except:
            obj_dep = Department.objects.create(title=departmentToChange, create_user=usr)
            Relationship.setRelRelationship(comp, obj_dep, usr, type='hierarchy')

        obj_dep.setAttributeValue({'NAME': departmentToChange}, usr)

        if not Vacancy.objects.filter(c2p__parent=obj_dep.pk).exists():
            try:
                vac = Vacancy.objects.create(title='VACANCY_FOR_ORGANIZATION_ID:'+str(obj_dep.pk), create_user=usr)
                trans_real.activate('ru') #activate russian locale
                res = vac.setAttributeValue({'NAME':'Работник(ца)'}, usr)
                trans_real.deactivate() #deactivate russian locale

                if not res:
                    vac.delete()
                    return False
                try:
                    Relationship.setRelRelationship(obj_dep, vac, usr, type='hierarchy')
                    #add current user to default Vacancy
                except Exception as e:
                    print('Can not create Relationship between Vacancy ID:' + str(vac.pk) + 'and Department ID:'+
                            str(obj_dep.pk) + '. The reason is:' + str(e))
                    vac.delete()
            except Exception as e:
                print('Can not create Vacancy for Department ID:' + str(obj_dep.pk) + '. The reason is:' + str(e))
                pass

        obj_dep.reindexItem()
        vac.reindexItem()

    departments = func.getActiveSQS().models(Department).filter(tpp=tpp).order_by('text')
    attr = ('NAME', 'SLUG')

    departmentsList, page = func.setPaginationForSearchWithValues(departments, *attr, page_num=10, page=page)

    paginator_range = func.getPaginatorRange(page)
    url_paginator = "companies:tab_structure_paged"

    permissionsList = comp.getItemInstPermList(request.user)

    templateParams = {
        'departmentsList': departmentsList,
        'permissionsList': permissionsList,
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'url_parameter': tpp,
    }

    return render_to_response('Tpp/tabStructure.html', templateParams, context_instance=RequestContext(request))

def _tabsStaff(request, tpp, page=1):
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
        try:
            curr_user_cab = Cabinet.objects.get(user=request.user)
            if curr_user_cab.pk != cabinetToDetach:
                Relationship.objects.filter(parent__c2p__parent__c2p__parent=tpp, child=cabinetToDetach,
                                            type='relation').delete()
        except Exception as e:
            pass

    # add a new user to department
    userEmail = request.POST.get('userEmail', '')
    if len(userEmail):
        departmentName = request.POST.get('departmentName', '')
        vacancyName = request.POST.get('vacancyName', '')
        isAdmin = int(request.POST.get('isAdmin', 0))
        if len(departmentName):
            try:
                dep = Department.objects.get(c2p__parent=tpp, item2value__attr__title='NAME', item2value__title=departmentName)
                try:
                    vac = Vacancy.objects.get(c2p__parent=dep, item2value__attr__title='NAME', item2value__title=vacancyName)
                except: #if this Department hasn't this Vacancy then add Vacancy to Department
                    vac = Vacancy.objects.create(title='VACANCY_FOR_DEPARTMENT_ID:'+str(dep.pk), create_user=request.user)
                    vac.setAttributeValue({'NAME': vacancyName}, request.user)
                    Relationship.objects.create(parent=dep, child=vac, type='hierarchy', create_user=request.user)

                usr = User.objects.get(email=userEmail)
                #if User already works in the Organization, don't allow to connect him to the Company
                if not Cabinet.objects.filter(user=usr, c2p__parent__c2p__parent__c2p__parent=tpp).exists():
                    cab, res = Cabinet.objects.get_or_create(user=usr, create_user=usr)
                    if res:
                        try:
                            cab.setAttributeValue({'USER_FIRST_NAME': usr.first_name, 'USER_MIDDLE_NAME':'',\
                                                'USER_LAST_NAME': usr.last_name, 'EMAIL': usr.email}, usr)
                            group = Group.objects.get(name='Company Creator')
                            usr.is_manager = True
                            usr.save()
                            group.user_set.add(usr)
                        except Exception as e:
                            print('Can not set attributes for Cabinet ID:'+cab.pk+'. The reason is:'+e)

                    if isAdmin:
                        flag = True
                    else:
                        flag = False
                    Relationship.objects.get_or_create(parent=vac, child=cab, is_admin=flag, type='relation', create_user=request.user)
                else:
                    pass
            except:
                logger.exception("Error in tab staff.",  exc_info=True)
                pass

    cabinets = Cabinet.objects.filter(c2p__parent__c2p__parent__c2p__parent=tpp).distinct()
    attr = ('USER_FIRST_NAME', 'USER_MIDDLE_NAME', 'USER_LAST_NAME', 'EMAIL', 'IMAGE', 'SLUG')
    workersList, page = func.setPaginationForSearchWithValues(cabinets, *attr, page_num=10, page=page)

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
                        cab_att['STATUS'] = ['Active']
                        break

    paginator_range = func.getPaginatorRange(page)
    url_paginator = "companies:tab_staff_paged"

    #create full list of Company's Departments
    departments = func.getActiveSQS().models(Department).filter(tpp=tpp).order_by('text')

    dep_lst = [dep.pk for dep in departments]

    if len(dep_lst) == 0:
        departmentsList = []
    else:
        departmentsList = Item.getItemsAttributesValues(('NAME',), dep_lst)

    #create list of Company's Vacancies
    vacancies = func.getActiveSQS().models(Vacancy).filter(tpp=tpp).order_by('text')

    vac_lst = [vac.pk for vac in vacancies]

    if len(vac_lst) == 0:
        vacanciesList = []
    else:
        vacanciesList = Item.getItemsAttributesValues(('NAME',), vac_lst)

    comp = Tpp.objects.get(pk=tpp)
    permissionsList = comp.getItemInstPermList(request.user)

    templateParams = {
        'workersList': workersList,
        'departmentsList': departmentsList, #list for adding user form
        'vacanciesList': vacanciesList,     #list for adding user form
        'permissionsList': permissionsList,
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'url_parameter': tpp,
    }

    return render_to_response('Tpp/tabStaff.html', templateParams, context_instance=RequestContext(request))

