from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _
from appl.models import *
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from core.models import Item
from appl import func
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import modelformset_factory
from tppcenter.forms import ItemForm, Test, BasePages
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from haystack.query import SQ, SearchQuerySet
import json
from core.tasks import addNewTpp
from django.conf import settings
from django.utils import timezone
from datetime import datetime
from django.core.cache import cache


def get_tpp_list(request, page=1, item_id=None, my=None, slug=None):


   # if slug and  not Value.objects.filter(item=item_id, attr__title='SLUG', title=slug).exists():
    #     slug = Value.objects.get(item=item_id, attr__title='SLUG').title
     #    return HttpResponseRedirect(reverse('tpp:detail',  args=[slug]))
    if item_id:
       if not Item.active.get_active().filter(pk=item_id).exists():
         return HttpResponseNotFound()

    cabinetValues = func.getB2BcabinetValues(request)
    description = ''
    title = ''
    current_company = request.session.get('current_company', False)

    if current_company:
        current_company = Organization.objects.get(pk=current_company).getAttributeValues("NAME")

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
            'current_company': current_company,
            'styles': styles,
            'search': request.GET.get('q', ''),
            'addNew': reverse('tpp:add'),
            'cabinetValues': cabinetValues,
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
    query = request.GET.urlencode()

    if not my and not request.user.is_authenticated():
        if query.find('sortField') == -1 and query.find('order') == -1 and query.find('filter') == -1:
            cached = cache.get(cache_name)

    if not cached:

        q = request.GET.get('q', '')

        if not my:
            filters, searchFilter = func.filterLive(request)

            sqs = func.getActiveSQS().models(Tpp)

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

            if current_organization:
                tpp = SearchQuerySet().models(Tpp).filter(id=current_organization)

                if q != '':
                   tpp = tpp.filter(title=q)

                tpp.order_by('-obj_create_date')

                url_paginator = "tpp:my_main_paginator"
                params = {}
            else:
                raise ObjectDoesNotExist('you need check company')

        attr = ('NAME', 'IMAGE', 'ADDRESS', 'SITE_NAME', 'TELEPHONE_NUMBER', 'FAX', 'INN', 'DETAIL_TEXT', 'FLAG', 'SLUG')

        result = func.setPaginationForSearchWithValues(tpp, *attr, page_num=5, page=page)

        tppList = result[0]
        tpp_ids = [id for id in tppList.keys()]
        if request.user.is_authenticated():
            items_perms = func.getUserPermsForObjectsList(request.user, tpp_ids, Tpp.__name__)
        else:
            items_perms = ""
        countries = Country.objects.filter(p2c__child__in=tpp_ids).values('p2c__child', 'pk')
        countries_id = [country['pk'] for country in countries]
        countriesList = Item.getItemsAttributesValues(("NAME", 'FLAG'), countries_id)
        country_dict = {}

        for country in countries:
            country_dict[country['p2c__child']] = country['pk']

        for id, tpp in tppList.items():
            toUpdate = {'COUNTRY_NAME': countriesList[country_dict[id]].get('NAME', [0]) if country_dict.get(id, 0) else [0],
                        'COUNTRY_FLAG': countriesList[country_dict[id]].get('FLAG', [0]) if country_dict.get(id, 0) else [0],
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

        if not my and not request.user.is_authenticated():
            if query.find('sortField') == -1 and query.find('order') == -1 and query.find('filter') == -1:
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
        tppValues = tpp.getAttributeValues(*('NAME', 'DETAIL_TEXT', 'FLAG', 'IMAGE'))
        description = tppValues.get('DETAIL_TEXT', False)[0] if tppValues.get('DETAIL_TEXT', False) else ""
        description = func.cleanFromHtml(description)
        title = tppValues.get('NAME', False)[0] if tppValues.get('NAME', False) else ""


        if not tppValues.get('FLAG', False):
           try:
               country = Country.objects.get(p2c__child=tpp, p2c__type='dependence').getAttributeValues(*('FLAG', 'NAME'))
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

    cabinetValues = func.getB2BcabinetValues(request)

    current_company = request.session.get('current_company', False)

    if current_company:
        current_company = Organization.objects.get(pk=current_company).getAttributeValues("NAME")

    current_section = _("Tpp")

    if action == 'add':
        tppPage = addTpp(request)
    else:
        tppPage = updateTpp(request, item_id)

    if isinstance(tppPage, HttpResponseRedirect) or isinstance(tppPage, HttpResponse):
        return tppPage

    templateParams = {
        'formContent': tppPage,
        'current_company':current_company,
        'current_section': current_section,
        'cabinetValues': cabinetValues
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
        values.update(request.FILES)

        form = ItemForm('Tpp', values=values, id=item_id)
        form.clean()

        if form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addNewTpp.delay(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id,
                            lang_code=settings.LANGUAGE_CODE)

            return HttpResponseRedirect(reverse('tpp:main'))

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
        news = func.getActiveSQS().models(News).filter(tpp=tpp)
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
        tenders = func.getActiveSQS().models(Tender).filter(tpp=tpp)
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
        exhibition = func.getActiveSQS().models(Exhibition).filter(tpp=tpp)
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
