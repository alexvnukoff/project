__author__ = 'user'

from django import template
from django.template import RequestContext, loader
from appl.models import Tpp, Company, Product, Notification
from django.utils.translation import ugettext as _

register = template.Library()

@register.inclusion_tag('InclusionTags/bottomAnalytic.html')
def setAnalytic():
    return {
        'productCount': Product.objects.count(),
        'companiesCount': Company.objects.count(),
        'partnersCount': Tpp.objects.count()
    }




