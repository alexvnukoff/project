__author__ = 'user'

from django import template
from appl import func
from django.template import RequestContext, loader
from appl.models import Tpp, Company, Product, Notification
from django.utils.translation import ugettext as _


register = template.Library()

@register.inclusion_tag('AdvTop/tops.html', takes_context=True)
def getTopOnPage(context, item_id=None):

    request = context.get('request')


    if item_id:
        filterAdv = func.getDeatailAdv(item_id)
    else:
        filterAdv = func.getListAdv(request)


    return {'modelTop': func.getTops(request, filter=filterAdv) }

