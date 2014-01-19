from django import template
from collections import OrderedDict
register = template.Library()


@register.filter(name='sort')
def sort(value):
    sorted_dict = OrderedDict(sorted(value.items(), reverse=False))

    return sorted_dict.items()


