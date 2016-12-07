import hashlib

from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.timezone import make_aware, is_naive, get_current_timezone, now
from django.utils.translation import ugettext as _

from b24online.models import Chamber, InnovationProject, News, Company, BusinessProposal, Exhibition, Country, Branch, \
    Organization, B2BProduct, Banner, B2BProductCategory, BusinessProposalCategory
from b24online.search_indexes import CountryIndex, ChamberIndex, BranchIndex, B2bProductCategoryIndex, \
    BusinessProposalCategoryIndex, SearchEngine, B2cProductCategoryIndex
from centerpokupok.models import B2CProduct, B2CProductCategory
from jobs.models import Requirement


def get_paginator_range(page):
    """
    Method that get page object and return paginatorRange ,
    help to  display properly pagination
    Example
    result = func.getItemsListWithPagination("News", "NAME", "Active_From", "DETAIL_TEXT", "IMAGE", page=4)
    newsList = result[0]
    page = result[1]
    paginator_range = func.getPaginatorRange(page) Pass this object to template

    """
    if page.number - 2 > 0:
        start = page.number - 2
    else:
        start = 1
    if start + 5 <= page.paginator.num_pages:
        end = start + 5
    else:
        end = page.paginator.num_pages + 1

    paginator_range = range(start, end)
    return paginator_range

def currency_symbol(currency):
    if not currency:
        return ""

    symbols = {
        'EUR': '€',
        'USD': '$',
        'ILS': '₪',
        'NIS': '₪',
    }

    return symbols.get(currency.upper(), currency)


def publish_realtime(publication_type, **params):
    import redis
    from django.conf import settings
    import json

    ORDERS_FREE_LOCK_TIME = getattr(settings, 'ORDERS_FREE_LOCK_TIME', 0)
    ORDERS_REDIS_HOST = getattr(settings, 'ORDERS_REDIS_HOST', 'localhost')
    ORDERS_REDIS_PORT = getattr(settings, 'ORDERS_REDIS_PORT', 6379)
    ORDERS_REDIS_PASSWORD = getattr(settings, 'ORDERS_REDIS_PASSWORD', None)
    ORDERS_REDIS_DB = getattr(settings, 'ORDERS_REDIS_DB', 0)

    # опять удобства
    service_queue = redis.StrictRedis(
        host=ORDERS_REDIS_HOST,
        port=ORDERS_REDIS_PORT,
        db=ORDERS_REDIS_DB,
        password=ORDERS_REDIS_PASSWORD
    ).publish

    service_queue(publication_type, json.dumps(params))



def organizationIsCompany(item_id):
    if Company.objects.filter(p2c__child=item_id, p2c__type='dependence').exists():
        return True

    return False



def get_banner(block, site_id, filter_adv=None):
    # TODO optimize the function for batch
    banner_queryset = Banner.objects.filter(
        block__code=block,
        is_active=True,
        site=site_id,
        dates__contains=now().date()
    )
    targeting_filter = None

    for target_model, target_items in filter_adv.items():
        if not target_items:
            continue

        tmp_filter = Q(
            targets__content_type__model=target_model.lower(),
            targets__object_id__in=target_items
        )

        targeting_filter = tmp_filter if targeting_filter is None else targeting_filter | tmp_filter

    if targeting_filter is not None:
        banner_queryset = banner_queryset.filter(targeting_filter)

    return banner_queryset.order_by('?').first()


def get_tops(filterAdv=None):
    """
        Get context advertisement items depended on received filter

        dict filterAdv - advertisement filter , can include countries organizations or branches
                (get it from getDeatailAdv() or getListAdv() )
    """
    is_adv_empty = True

    models = {
        Chamber: {
            'count': 1,  # Limit of this type to fetch
            'text': _('Organizations'),  # Title
            'detailUrl': 'tpp:detail',  # URL namespace to detail page of this type of item
            'select_related': None,
            'prefetch_related': ['countries']
        },
        News: {
            'count': 1,  # Limit of this type to fetch
            'text': _('News'),  # Title
            'detailUrl': 'news:detail',  # URL namespace to detail page of this type of item
            'select_related': ['country'],
            'prefetch_related': ['organization', 'organization__countries']
        },
        B2BProduct: {
            'count': 1,  # Limit of this type to fetch
            'text': _('Products'),  # Title
            'detailUrl': 'products:detail',  # URL namespace to detail page of this type of item
            'select_related': None,
            'prefetch_related': ['company', 'company__countries']
        },
        InnovationProject: {
            'count': 1,
            'text': _('Innovation Projects'),
            'detailUrl': 'innov:detail',  # URL namespace to detail page of this type of item
            'select_related': None,
            'prefetch_related': ['organization', 'organization__countries']
        },
        Company: {
            'count': 1,
            'text': _('Companies'),
            'detailUrl': 'companies:detail',  # URL namespace to detail page of this type of item
            'select_related': None,
            'prefetch_related': ['countries']
        },
        BusinessProposal: {
            'count': 1,
            'text': _('Business Proposals'),
            'detailUrl': 'proposal:detail',  # URL namespace to detail page of this type of item
            'select_related': ['country'],
            'prefetch_related': ['organization', 'organization__countries']
        },
        Requirement: {
            'count': 3,
            'text': _('Job requirements'),
            'detailUrl': 'vacancy:detail',  # URL namespace to detail page of this type of item
            'select_related': ['country'],
            'prefetch_related': ['vacancy__department__organization', 'vacancy__department__organization__countries']
        },
        Exhibition: {
            'count': 1,
            'text': _('Exhibitions'),
            'detailUrl': 'exhibitions:detail',  # URL namespace to detail page of this type of item
            'select_related': ['country'],
            'prefetch_related': ['organization', 'organization__countries']
        }

    }

    for model, modelDict in models.items():
        # Get all active context advertisement of some specific type
        queryset = model.objects.filter(
            context_advertisements__is_active=True,
            context_advertisements__content_type__model=model.__name__.lower(),
            context_advertisements__dates__contains=now().date()
        )

        targeting_filter = None

        # Do we have some filters depended on current page ?
        for target_model, target_items in filterAdv.items():
            if not target_items:
                continue

            tmp_filter = Q(
                context_advertisements__targets__content_type__model=target_model.lower(),
                context_advertisements__targets__object_id__in=target_items
            )

            targeting_filter = tmp_filter if targeting_filter is None else targeting_filter | tmp_filter

        if targeting_filter is not None:
            queryset = queryset.filter(targeting_filter)

        if modelDict['select_related'] is not None:
            queryset = queryset.select_related(*modelDict['select_related'])

        if modelDict['prefetch_related'] is not None:
            queryset = queryset.prefetch_related(*modelDict['prefetch_related'])

        modelDict['queryset'] = queryset.order_by('?')[:int(modelDict['count'])]

        if is_adv_empty and modelDict['queryset']:
            is_adv_empty = False

    if is_adv_empty:
        return None

    return models


def get_detail_adv_filter(obj):
    cache_key = "adv_filter:detail:%s:%s" % (obj.__class__, obj.pk)
    filter_by_model = cache.get(cache_key)

    if not filter_by_model:
        filter_by_model = {}

        org = getattr(obj, 'organization', None)
        company = getattr(obj, 'company', None) if not isinstance(obj, Organization) else None
        branches = getattr(obj, 'branches', None)

        if org is not None:
            if isinstance(org, Chamber):
                filter_by_model[Chamber.__name__] = [org.id]
            elif org.parent_id:
                filter_by_model[Chamber.__name__] = [org.parent_id]
        elif company:
            filter_by_model[Branch.__name__] = list(company.branches.all().values_list('pk', flat=True))

            if company.parent_id:
                filter_by_model[Chamber.__name__] = [company.parent_id]

        if branches is not None:
            if Branch.__name__ in filter_by_model:
                filter_by_model[Branch.__name__] += list(branches.all().values_list('pk', flat=True))
            else:
                filter_by_model[Branch.__name__] = list(branches.all().values_list('pk', flat=True))

        cache.set(cache_key, filter_by_model, 60 * 1)

    return filter_by_model


def get_list_adv_filter(request):
    cache_key = "adv_filter:list:%s" % hashlib.md5(request.META['QUERY_STRING'].encode('utf-8')).hexdigest()
    list_filter = cache.get(cache_key)

    if not list_filter:
        filter_by_model = {
            'chamber': [Chamber.__name__, []],
            'country': [Country.__name__, []],
            'branches': [Branch.__name__, []],
        }

        countries = []

        for filter_key, filter_items in filter_by_model.items():
            for pk in request.GET.getlist('filter[' + filter_key + '][]', []):
                try:
                    filter_items[1].append(int(pk))
                except ValueError:
                    continue

            # Add filter of countries of each tpp
            if filter_items[0] == Chamber.__name__ and len(filter_items[1]) > 0:
                countries + list(Country.objects \
                                 .filter(organizations__pk__in=filter_items[1]).values_list('pk', flat=True))

        filter_by_model['country'][1] += countries
        list_filter = dict(filter_by_model.values())
        cache.set(cache_key, list_filter, 60 * 5)

    return list_filter


def show_toolbar(request):
    if request.user.is_authenticated():
        if request.user.is_superuser:
            return True

    return False



def autocomplete_filter(filter_key, q, page):
    filters = {
        'countries': {
            'model': Country,
            'index_model': CountryIndex,
        },
        'country': {
            'model': Country,
            'index_model': CountryIndex,
        },
        'chamber': {
            'model': Chamber,
            'index_model': ChamberIndex,
        },
        'organization': {
            'model': Chamber,
            'index_model': ChamberIndex,
        },
        'branches': {
            'model': Branch,
            'index_model': BranchIndex,
        },
        'b2b_categories': {
            'model': B2BProductCategory,
            'index_model': B2bProductCategoryIndex,
        },
        'b2c_categories': {
            'model': B2CProductCategory,
            'index_model': B2cProductCategoryIndex,
        },
        'bp_categories': {
            'model': BusinessProposalCategory,
            'index_model': BusinessProposalCategoryIndex,
        }
    }

    model_dict = filters.get(filter_key, None)

    if model_dict is None:
        return None

    if (len(q) != 0 and len(q) <= 2) or page < 0:
        return None

    if len(q) > 2:
        s = SearchEngine(doc_type=model_dict['index_model']).query('match', name_auto=q)
        fields = [field.name for field in model_dict['model']._meta.get_fields()]

        if 'is_active' in fields:
            s = s.query('match', is_active=True)

        if 'is_deleted' in fields:
            s = s.query('match', is_deleted=False)

        paginator = Paginator(s, 10)
        object_ids = [obj.django_id for obj in paginator.page(page).object_list]

        return model_dict['model'].objects.filter(pk__in=object_ids), paginator.count
    else:
        objects = model_dict['model'].objects.all()
        paginator = Paginator(objects, 10)

        return paginator.page(page).object_list, paginator.count


def verify_ipn_request(payment_obj):
    if not payment_obj.item_number:
        return True, 'Item id was not provided'

    try:
        product = B2CProduct.objects.get(pk=payment_obj.item_number)
    except ObjectDoesNotExist:
        return True, "B2C product does not exist. (%s)" % payment_obj.item_number

    if product.company.company_paypal_account != payment_obj.business:
        return True, "Invalid receiver_email. (%s)" % payment_obj.receiver_email

    return False, None

