__author__ = 'user'

from django import template
from appl import func
from django.conf import settings


register = template.Library()

@register.inclusion_tag('AdvTop/tops.html', takes_context=True)
def getTopOnPage(context, item_id=None):

    request = context.get('request')


    if item_id:
        filterAdv = func.getDeatailAdv(item_id)
    else:
        filterAdv = func.getListAdv(request)


    return {'modelTop': func.getTops(request, filterAdv) }

@register.inclusion_tag('AdvBanner/banners.html', takes_context=True)
def getBanners(context, item_id=None, *places):

    request = context.get('request')

    if item_id:
        filterAdv = func.getDeatailAdv(item_id)
    else:
        filterAdv = func.getListAdv(request)

    return {'banners': func.getBanners(places, settings.SITE_ID, filterAdv)}



