from django.shortcuts import render
from django.shortcuts import render_to_response, get_object_or_404
from appl.models import *
from django.http import Http404, HttpResponseRedirect, HttpResponse
from core.models import Value, Item, Attribute, Dictionary, AttrTemplate, Relationship
from appl import func
from django.core.exceptions import ValidationError
from django.forms.models import modelformset_factory
from django.db.models import get_app, get_models
from tppcenter.forms import ItemForm, Test, BasePages
from django.template import RequestContext, loader
from datetime import datetime
from django.utils.timezone import now
from django.core.urlresolvers import reverse
from tpp.SiteUrlMiddleWare import get_request
from celery import shared_task, task
from haystack.query import SQ, SearchQuerySet
import json
from core.tasks import addNewTpp
from django.conf import settings



def get_tpp_list(request, page=1, item_id=None):


    if item_id is None:
        tppPage = _tppContent(request, page)
    else:
        tppPage = _tppDetailContent(request, item_id)

    styles = [
        settings.STATIC_URL + 'tppcenter/css/news.css',
        settings.STATIC_URL + 'tppcenter/css/company.css',
        settings.STATIC_URL + 'tppcenter/css/tpp.reset.css'
    ]
    scripts = []

    if not request.is_ajax():
        user = request.user
        if user.is_authenticated():
            notification = len(Notification.objects.filter(user=request.user, read=False))
            if not user.first_name and not user.last_name:
                user_name = user.email
            else:
                user_name = user.first_name + ' ' + user.last_name
        else:
            user_name = None
            notification = None
        current_section = "Companies"



        templateParams = {
            'user_name': user_name,
            'current_section': current_section,
            'tppPage': tppPage,
            'notification': notification,
            'scripts': scripts,
            'styles': styles,
            'search': request.GET.get('q', '')
        }

        return render_to_response("Tpp/index.html", templateParams, context_instance=RequestContext(request))
    else:
        return HttpResponse(json.dumps({'styles': styles, 'scripts': scripts, 'content': tppPage}))


def _tppContent(request, page=1):

    #tpp = Tpp.active.get_active().order_by('-pk')

    filters, searchFilter = func.filterLive(request)

    sqs = SearchQuerySet().models(Tpp)

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


    tpp = sqs.order_by(*order)

    result = func.setPaginationForSearchWithValues(tpp, *('NAME', 'IMAGE', 'ADDRESS', 'SITE_NAME',
                                                               'TELEPHONE_NUMBER', 'FAX', 'INN', 'DETAIL_TEXT', 'FLAG',
                                                               'SLUG'),      page_num=5, page=page)

    tppList = result[0]
    tpp_ids = [id for id in tppList.keys()]
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

    url_paginator = "tpp:paginator"
    template = loader.get_template('Tpp/contentPage.html')

    templateParams = {
        'tppList': tppList,
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'sortField1': sortField1,
        'sortField2': sortField2,
        'order1': order1,
        'order2': order2
    }


    context = RequestContext(request, templateParams)

    return template.render(context)


def _tppDetailContent(request, item_id):

    tpp = get_object_or_404(Tpp, pk=item_id)
    tppValues = tpp.getAttributeValues(*('NAME', 'DETAIL_TEXT', 'FLAG', 'IMAGE'))


    if not tppValues.get('FLAG', False):
       country = Country.objects.get(p2c__child=tpp).getAttributeValues(*('FLAG', 'NAME'))
    else:
       country = ""

    template = loader.get_template('Tpp/detailContent.html')
    context = RequestContext(request, {'tppValues': tppValues, 'country': country, 'item_id' : item_id})

    return template.render(context)

def addTpp(request):
    form = None

    if request.POST:
        func.notify("item_creating", 'notification', user=request.user)
        user = request.user

        Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
        pages = Page(request.POST, request.FILES, prefix="pages")

        values = _getValues(request)

        form = ItemForm('Tpp', values=values)
        form.clean()

        if form.is_valid() and pages.is_valid():
            addNewTpp(request.POST, request.FILES, user, settings.SITE_ID)
            return HttpResponseRedirect(reverse('tpp:main'))


    return render_to_response('Tpp/addForm.html', {'form': form},
                              context_instance=RequestContext(request))


def updateTpp(request, item_id):


    if request.method != 'POST':
        Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
        pages = Page(request.POST, request.FILES, prefix="pages", parent_id=item_id)
        pages = pages.queryset

        form = ItemForm('Tpp', id=item_id)

    if request.POST:
        func.notify("item_creating", 'notification', user=request.user)

        user = request.user
        Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
        pages = Page(request.POST, request.FILES, prefix="pages")


        values = _getValues(request)


        form = ItemForm('Tpp', values=values, id=item_id)
        form.clean()

        if form.is_valid() and pages.is_valid() :
            addNewTpp(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id)
            return HttpResponseRedirect(reverse('tpp:main'))

    return render_to_response('Tpp/addForm.html', {'form': form, 'pages': pages},
                              context_instance=RequestContext(request))


def _getValues(request):
    values = {}
    values['NAME'] = request.POST.get('NAME', "")
    values['IMAGE'] = request.FILES.get('IMAGE', "")
    values['FLAG'] = request.FILES.get('FLAG', "")
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




def _tabsCompanies(request, tpp, page=1):

    companies = SearchQuerySet().models(Company).filter(tpp=tpp)
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
    }

    return render_to_response('Tpp/tabCompanies.html', templateParams, context_instance=RequestContext(request))

def _tabsNews(request, tpp, page=1):

    news = SearchQuerySet().models(News).filter(tpp=tpp)
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


    templateParams = {
    }

    return render_to_response('Tpp/tabTenders.html', templateParams, context_instance=RequestContext(request))

def _tabsExhibitions(request, tpp, page=1):


    templateParams = {
    }

    return render_to_response('Tpp/tabExhibitions.html', templateParams, context_instance=RequestContext(request))