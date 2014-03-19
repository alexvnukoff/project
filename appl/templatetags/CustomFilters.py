from django import template
from collections import OrderedDict
from django.core.urlresolvers import reverse
from copy import copy
from appl.func import currencySymbol
from tpp.SiteUrlMiddleWare import get_request
import datetime
from django.template import Node, TemplateSyntaxError
from lxml.html.clean import clean_html
from appl import func
from appl.models import Tpp, Company, Product
from appl.models import Notification
import lxml
from urllib.parse import urlencode

register = template.Library()


@register.filter(name='sort')
def sort(value):
    if value:
          sorted_dict = OrderedDict(sorted(value.items(), reverse=False))
          return sorted_dict.items()
    else:
        return ""

@register.filter(name='discountDiff')
def discountDiff(value, discount):
    try:
        value = float(value)
        discount = float(discount)
        price = '{0:.2f}'.format(value - (value - (value * discount) / 100))
        return '{0:,}'.format(float(price))
    except Exception:
        return 0

@register.filter(name='discountPrice')
def discountPrice(value, discount):
    try:
        value = float(value)
        discount = float(discount)
        price = '{0:.2f}'.format(value - (value * discount) / 100)
        return '{0:,}'.format(float(price))

    except Exception:
        return 0

@register.filter(name='formatPrice')
def formatPrice(value):
    try:
        value = float(value)
        price = '{0:.2f}'.format(value)
        return '{0:,}'.format(float(price))
    except Exception:
        return 0

@register.filter(name='getSymbol')
def getSymbol(value):

    return currencySymbol(value)

@register.filter(name='split')
def split(str, splitter):
    return str.split(splitter)




@register.filter(name='cleanHtml')
def cleanHtml(value):

    if len(value) > 0:
        return clean_html(value)





@register.filter(name='makeDate')
def makeDate(value):

    if value:
        try:
            date = datetime.datetime.strptime(value, "%Y-%m-%d")
            return date
        except Exception:
            pass
        try:
            date = datetime.datetime.strptime(value, "%m/%d/%Y")
            return date
        except Exception:
            pass


class DynUrlNode(template.Node):
    def __init__(self, *args):
        self.name_var = args[0]
        self.parametrs = args[1]

        if len(args) > 2:
            self.new_parametr = args[2]


    def render(self, context):
        name = template.Variable(self.name_var).resolve(context)

        try:
            parametrs = copy(template.Variable(self.parametrs).resolve(context))
        except Exception:
            parametrs = []
        if not isinstance(parametrs, list):
            l = list()
            l.append(parametrs)
            parametrs = copy(l)

        try:
            new_parametr = copy(template.Variable(self.new_parametr).resolve(context))
            if not isinstance(new_parametr, list):
                l = list()
                l.append(new_parametr)
                new_parametr = copy(l)
            parametrs.extend(new_parametr)
        except Exception:
            pass



        request = get_request()
        query_set = None
        if len(request.GET) > 0:
            query_set = urlencode(request.GET)


        url = reverse(name, args=parametrs) + '?'+ query_set if query_set else reverse(name, args=parametrs)
        return url

@register.tag
def dynurl(parser, token):
    args = token.split_contents()
    return DynUrlNode(*args[1:])


@register.assignment_tag()
def resolve(lookup, target):
    try:
        if isinstance(lookup, list):
            return lookup[int(target)]
        else:
            return lookup[target]

    except Exception as e:
        return None





class RangeNode(Node):
    def __init__(self, parser, range_args, context_name):
        self.template_parser = parser
        self.range_args = range_args
        self.context_name = context_name

    def render(self, context):

        resolved_ranges = []
        for arg in self.range_args:
            compiled_arg = self.template_parser.compile_filter(arg)
            resolved_ranges.append(compiled_arg.resolve(context, ignore_failures=True))
        context[self.context_name] = range(*resolved_ranges)
        return ""

@register.tag
def mkrange(parser, token):
    """
    Accepts the same arguments as the 'range' builtin and creates
    a list containing the result of 'range'.

    Syntax:
        {% mkrange [start,] stop[, step] as context_name %}

    For example:
        {% mkrange 5 10 2 as some_range %}
        {% for i in some_range %}
          {{ i }}: Something I want to repeat\n
        {% endfor %}

    Produces:
        5: Something I want to repeat
        7: Something I want to repeat
        9: Something I want to repeat
    """

    tokens = token.split_contents()
    fnctl = tokens.pop(0)

    def error():
        raise TemplateSyntaxError( "%s accepts the syntax: {%% %s [start,] " +\
                "stop[, step] as context_name %%}, where 'start', 'stop' " +\
                "and 'step' must all be integers." %(fnctl, fnctl))
    range_args = []
    while True:
        if len(tokens) < 2:
            error()

        token = tokens.pop(0)

        if token == "as":
            break

        range_args.append(token)

    if len(tokens) != 1:
        error()

    context_name = tokens.pop()

    return RangeNode(parser, range_args, context_name)

@register.simple_tag
def productCount():
    return func.getActiveSQS().models(Product).count()

@register.simple_tag
def companiesCount():
    return func.getActiveSQS().models(Company).count()

@register.simple_tag
def partnersCount():
    return func.getActiveSQS().models(Tpp).count()

@register.assignment_tag
def getOwner(item):

    if not item:
        return None

    obj = func.getActiveSQS().filter(django_id=item)[0]

    if not obj:
        return None

    if obj.tpp:
        return {'type': 'tpp', 'id': obj.tpp}


    if obj.company:
        return {'type': 'company', 'id': obj.company}

    return None


@register.simple_tag(name='userName', takes_context=True)
def setUserName(context):
    request = context['request']
    user = request.user
    if user.is_authenticated():

        if not user.first_name and not user.last_name:
            user_name = user.email
        else:
            user_name = user.first_name + ' ' + user.last_name
    else:
        user_name = None
        notification = None
    return user_name

@register.simple_tag(name='notif',takes_context=True)
def setNotification(context):
    request = context['request']
    user = request.user
    if user.is_authenticated():
        notification = Notification.objects.filter(user=request.user, read=False).count()
    else:
        notification = None
    return notification


