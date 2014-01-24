from django import template
from collections import OrderedDict
from django.core.urlresolvers import reverse
from copy import copy
register = template.Library()



@register.filter(name='sort')
def sort(value):
    if value:
          sorted_dict = OrderedDict(sorted(value.items(), reverse=False))
          return sorted_dict.items()
    else:
        return ""


class DynUrlNode(template.Node):
    def __init__(self, *args):
        self.name_var = args[0]
        self.parametrs = args[1]
        self.new_parametr = args[2]

    def render(self, context):
        name = template.Variable(self.name_var).resolve(context)

        try:
            parametrs = copy(template.Variable(self.parametrs).resolve(context))
        except Exception:
            parametrs = []


        new_parametr = template.Variable(self.new_parametr).resolve(context)
        parametrs.append(new_parametr)


        return reverse(name, args=parametrs)

@register.tag
def dynurl(parser, token):
    args = token.split_contents()
    return DynUrlNode(*args[1:])


