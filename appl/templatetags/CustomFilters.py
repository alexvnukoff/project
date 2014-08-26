from collections import OrderedDict
from copy import copy

from django.utils.translation import trans_real
from lxml.html.clean import clean_html
from haystack.query import SQ, SearchQuerySet
from django.template import RequestContext, loader
from django.conf import settings
from django.template import Node, TemplateSyntaxError
from django.utils.html import escape
from django.core.urlresolvers import reverse
from django import template

from appl.func import currencySymbol
from appl import func
from appl.models import *
import tppcenter.urls


register = template.Library()


@register.filter(name='getSide')
def getSide(value):

    is_right = trans_real.get_language() == 'he' or trans_real.get_language() == 'ar'

    return is_right

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

    if value is not None and len(value) > 0:
        return clean_html(value)
    else:
        return ""





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
            query_set = request.GET.urlencode()


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
def modelCount(model, owner=None):

    klass = (globals()[model])

    #sqs = klass.active.get_active().all()
    sqs = func.getActiveSQS().models(klass)

    if isinstance(owner, int):
        sqs.filter(SQ(tpp=owner) | SQ(company=owner))

    return sqs.count()

@register.assignment_tag
def getOwner(item):

    if not item:
        return None

    obj = func.getActiveSQS().filter(django_id=item)

    if len(obj) == 0:
        return None
    else:
        obj = obj[0]


    if not obj:
        return None

    if obj.company:
        return {'type': 'company', 'id': obj.company}

    if obj.tpp:
        return {'type': 'tpp', 'id': obj.tpp}

    return None


@register.simple_tag()
def getLang():
    return trans_real.get_language()

@register.simple_tag(name='userName', takes_context=True)
def setUserName(context):
    request = context.get('request')

    user_name = ''

    if request.user.is_authenticated():
        try:
            cabinet = Cabinet.objects.get(user=request.user)
            cabinet = SearchQuerySet().models(Cabinet).filter(django_id=cabinet.pk)

            if cabinet.count() > 0 and cabinet[0].text != '':
                user_name = cabinet[0].text

        except ObjectDoesNotExist:
            pass

        if user_name == '':
            user_name = request.user.email


    return user_name

@register.simple_tag(name='notif', takes_context=True)
def setNotification(context):
    request = context.get('request')
    user = request.user
    if user.is_authenticated():
        notification = Notification.objects.filter(user=request.user, read=False).count()
    else:
        notification = ""
    return notification


@register.simple_tag(name='mail', takes_context=True)
def setMessage(context):
    request = context.get('request')
    user = request.user
    if user.is_authenticated():
        cab_pk = Cabinet.objects.get(user=request.user)
        message = Messages.objects.filter(c2p__parent=cab_pk, c2p__type='relation', was_read=False).count()
    else:
        message = ""
    return message


@register.simple_tag(name='flags', takes_context=True)
def setFlags(context, country, url_country, url_country_parametr):

  request = context.get('request')
  if len(url_country) > 0:
      url_country = url_country
  else:
      url_country  = 'home_country'

  country = country
  if len(url_country_parametr) > 0:
        url_country_parametr = url_country_parametr
  else:
      url_country_parametr = []
  flagList = func.getItemsList("Country", "NAME", "FLAG")

  template = loader.get_template('main/Flags.html')
  context = RequestContext(request, {'flagList': flagList, 'url_country': url_country, 'country': country,
                                     'url_country_parametr': url_country_parametr})
  flags = template.render(context)

  return flags


@register.simple_tag(name='logo', takes_context=True)
def setLogo(context):
  user_site = UserSites.objects.get(sites__id=settings.SITE_ID)
  user_logo = user_site.getAttributeValues('SITE_LOGO')
  if len(user_logo) > 0:
      return user_logo[0]


  return ""

@register.simple_tag(name='footer_text', takes_context=True)
def setLogo(context):
  user_site = UserSites.objects.get(sites__id=settings.SITE_ID)
  site_footer = user_site.getAttributeValues('DETAIL_TEXT')
  if len(site_footer) > 0:
      return site_footer[0]


  return ""



@register.simple_tag(name='categories', takes_context=True)
def setCategories(context):

  request = context.get('request')
  hierarchyStructure = Category.hierarchy.getTree(siteID=settings.SITE_ID)
  categories_id = [cat['ID'] for cat in hierarchyStructure]
  categories = Item.getItemsAttributesValues(("NAME",), categories_id)
  categotySelect = func.setStructureForHiearhy(hierarchyStructure, categories)


  template = loader.get_template('main/Category.html')
  context = RequestContext(request, {'categotySelect': categotySelect})
  categories_select = template.render(context)

  return categories_select

@register.simple_tag(name='countries', takes_context=True)
def setCountries(context):

  request = context.get('request')

  contrySorted = func.sortByAttr("Country", "NAME")
  sorted_id = [coun.pk for coun in contrySorted]
  countryList = Item.getItemsAttributesValues(("NAME",), sorted_id)

  template = loader.get_template('main/Country.html')
  context = RequestContext(request, {'countryList': countryList})
  categories_select = template.render(context)

  return categories_select


@register.simple_tag(name='right_tv', takes_context=True)
def rightTv(context):

  request = context.get('request')
  if request.resolver_match.namespace == 'innov':
      is_innov = True
      tvValues  = ""
  else:
      sqs = func.getActiveSQS().models(TppTV)
      if sqs.count() == 0:
          return ''
      else:
          sqs = sqs.order_by('-obj_create_date')[0]
          tvValues = Item.getItemsAttributesValues(('YOUTUBE_CODE', 'NAME', 'SLUG'), [sqs.pk])
          tvValues = tvValues[sqs.pk]
          is_innov = False
  template = loader.get_template('main/tv.html')
  context = RequestContext(request, {'tvValues': tvValues, 'is_innov': is_innov })
  tv = template.render(context)
  return tv


@register.simple_tag(takes_context=True)
def searchQuery(context):
    request = context.get('request')
    return escape(request.GET.get('q', ''))


@register.simple_tag(name='detail_page_to_tppcenter', takes_context=True)
def detail_page_to_tppcenter(context, url, slug=None):

    prefix = Site.objects.get(name='tppcenter').domain + '/'
    if slug:
        url = (reverse(viewname=url, urlconf=tppcenter.urls,  args=[slug], prefix=prefix))
    else:
        url = (reverse(viewname=url, urlconf=tppcenter.urls,   prefix=prefix))

    return 'http://' + url

