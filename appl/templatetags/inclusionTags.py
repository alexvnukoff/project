__author__ = 'user'

from django import template
from appl.models import Tpp, Company, Product

register = template.libraries

@register.inclusion_tag('InclusionTags/bottomAnalytic.html')
def setAnalytic():
    return {
        'productCount': Product.objects.count(),
        'companiesCount': Company.objects.count(),
        'partnersCount': Tpp.objects.count()
    }