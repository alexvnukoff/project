__author__ = 'user'

from django import template
from appl import func
from django.conf import settings
from appl.models import Organization
from core.models import Item
from haystack.query import SearchQuerySet
from django.utils.translation import gettext as _

register = template.Library()

@register.inclusion_tag('AdvTop/tops.html', takes_context=True)
def getTopOnPage(context, item_id=None):

    request = context.get('request')
    MEDIA_URL = context.get('MEDIA_URL', '')

    if item_id:
        filterAdv = func.getDeatailAdv(item_id)
    else:
        filterAdv = func.getListAdv(request)


    return {'MEDIA_URL': MEDIA_URL,  'modelTop': func.getTops(request, filterAdv) }

@register.inclusion_tag('AdvBanner/banners.html', takes_context=True)
def getBanners(context, item_id=None, *places):

    request = context.get('request')
    MEDIA_URL = context.get('MEDIA_URL', '')

    if item_id:
        filterAdv = func.getDeatailAdv(item_id)
    else:
        filterAdv = func.getListAdv(request)

    return {'MEDIA_URL': MEDIA_URL, 'banners': func.getBanners(places, settings.SITE_ID, filterAdv)}

@register.inclusion_tag('main/currentCompany.html', takes_context=True)
def getMyCompaniesList(context):

    request = context.get('request')

    if request.user.is_authenticated():

        if not request.user.first_name and not request.user.last_name:
            user_name = request.user.email
        else:
            user_name = request.user.first_name + ' ' + request.user.last_name
    else:
        user_name = None

    current_company = request.session.get('current_company', False)

    user_groups = request.user.groups.values_list('pk', flat=True)

    companies = Organization.objects.filter(community__in=user_groups)

    companies_ids = companies.values_list('pk', flat=True)

    sqs = SearchQuerySet().filter(django_id__in=companies_ids).order_by('title')

    companies_ids = [company.id for company in sqs]

    if len(companies_ids) > 0:
        companies = Item.getItemsAttributesValues('NAME', companies_ids)
    else:
        companies = {}

    current = companies.get(current_company, False)

    if user_name == '':
        user_name = _('Profile')

    return {'companies': companies, 'current': current, 'currentId': current_company, 'user': user_name}



