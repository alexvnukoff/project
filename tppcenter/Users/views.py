from haystack.backends import SQ
from haystack.query import SearchQuerySet
from appl import func
from appl.func import filterLive, getActiveSQS, setPaginationForSearchWithValues, getPaginatorRange
from appl.models import Product, Gallery, AdditionalPages, Company, Country, Category, Organization, Cabinet
from core.models import Item, Dictionary
from core.tasks import addProductAttrubute
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _
from django.utils.timezone import now
from tppcenter.forms import ItemForm, BasePhotoGallery, BasePages
import json


def get_users_list(request, page=1):




    description = ''
    title = ''


    usersPage = get_users_content(request, page)



    styles = []
    scripts = []


    if not request.is_ajax():
        current_section = _("Users")

        templateParams = {
            'current_section': current_section,
            'usersPage': usersPage,
            'scripts': scripts,
            'styles': styles,


            'description': description,
            'title': title
        }

        return render_to_response("Users/index.html", templateParams, context_instance=RequestContext(request))

    else:

        serialize = {
            'styles': styles,
            'scripts': scripts,
            'content': usersPage,
        }

        return HttpResponse(json.dumps(serialize))

def get_users_content(request, page=1):

    q = request.GET.get('q', '')

    filters, searchFilter = filterLive(request)

    sqs = SearchQuerySet().models(Cabinet).order_by('-obj_create_date')

    if len(searchFilter) > 0: #Got filter values
            sqs = sqs.filter(searchFilter)

    if q != '': #Search for content
        sqs = sqs.filter(SQ(title=q) | SQ(text=q) | SQ(email=q))

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

    users = sqs.order_by(*order)
    url_paginator = "users:paginator"

    params = {
        'filters': filters,
        'sortField1': sortField1,
        'sortField2': sortField2,
        'order1': order1,
        'order2': order2
    }
    attr = ('IMAGE', 'USER_FIRST_NAME', 'USER_LAST_NAME')
    result = setPaginationForSearchWithValues(users, *attr, page_num=12, page=page)

    userList = result[0]

    users_ids = [id for id in userList.keys()]

    countries = dict(Country.objects.filter(p2c__child__in=users_ids, p2c__type='relation').values_list('p2c__child', 'pk'))

    countries_ids = [id for user, id in countries.items()]


    countriesValues = Item.getItemsAttributesValues(("NAME", 'COUNTRY_FLAG'), countries_ids)

    for id, user in userList.items():
        if countries.get(id, False):
            user['COUNTRY_NAME'] = countriesValues.get(countries[id], {}).get('NAME', [0])
            user['COUNTRY_FLAG'] = countriesValues.get(countries[id], {}).get('COUNTRY_FLAG', [0])


    page = result[1]
    paginator_range = getPaginatorRange(page)


    template_page = 'Users/contentPage.html'

    template = loader.get_template(template_page)

    templateParams = {
        'userList': userList,
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,


    }

    templateParams.update(params)

    context = RequestContext(request, templateParams)
    rendered = template.render(context)

    return rendered





