# -*- encoding: utf-8 -*-

from collections import OrderedDict, Iterable
from copy import copy
from decimal import Decimal
import os
import datetime
import logging

from django.db import models
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.template.defaultfilters import stringfilter
from django.utils.translation import trans_real
from lxml.html.clean import clean_html
from django.utils.html import escape
from django.core.urlresolvers import reverse
from django import template

from appl.func import currency_symbol
from b24online.models import (Chamber, Notification, RegisteredEventType,
    RegisteredEvent)
from tpp.SiteUrlMiddleWare import get_request
from b24online.utils import GeoIPHelper

import b24online.urls

logger = logging.getLogger(__name__)

register = template.Library()


@register.filter()
def multiply(value, multiplier):
    if isinstance(value, str):
        return value * int(multiplier)

    if isinstance(multiplier, str):
        return int(value) * multiplier

    return Decimal(value) * Decimal(multiplier)


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
    return currency_symbol(value)


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

        url = reverse(name, args=parametrs) + '?' + query_set if query_set else reverse(name, args=parametrs)
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


@register.assignment_tag
def getOwner(item):
    org = getattr(item, 'organization', None) or getattr(item, 'company', None)

    if org:
        return {
            'type': 'tpp' if isinstance(org, Chamber) else 'company',
            'pk': org.pk
        }

    return None


@register.simple_tag()
def getLang():
    return trans_real.get_language()


# @register.simple_tag()
# def getCountry(obj):
#     return SearchQuerySet().filter(django_id=obj)[0].text


@register.simple_tag(name='userName', takes_context=True)
def set_user_name(context):
    request = context.get('request')

    user_name = ''

    if request.user.is_authenticated():
        try:
            if request.user.profile and request.user.profile.full_name:
                user_name = request.user.profile.full_name
            else:
                user_name = request.user.email

        except ObjectDoesNotExist:
            user_name = request.user.email

    return user_name


@register.simple_tag(takes_context=True)
def set_notification_count(context):
    request = context.get('request')
    user = request.user
    if user.is_authenticated():
        notification = Notification.objects.filter(user=request.user, read=False).count()
    else:
        notification = ""
    return notification


@register.simple_tag(takes_context=True)
def set_message_count(context):
    request = context.get('request')

    if request.user.is_authenticated():
        # cab_pk = request.user.objects.get(user=request.user)
        message = 0  # Messages.objects.filter(c2p__parent=cab_pk, c2p__type='relation', was_read=False).count()
    else:
        message = 0

    return message


@register.simple_tag(takes_context=True)
def search_query(context):
    request = context.get('request')
    return escape(request.GET.get('q', ''))


@register.simple_tag(name='detail_page_to_tppcenter')
def detail_page_to_tppcenter(url, *args):
    cache_name = "site:domain:b24online"
    prefix = cache.get(cache_name)

    if not prefix:
        prefix = Site.objects.get(name='b24online').domain + '/'
        cache.set(cache_name, prefix, 60 * 60 * 24 * 7)
    url = (reverse(viewname=url, urlconf=b24online.urls, args=args, prefix=prefix))

    return 'http://%s' % url


@register.assignment_tag(takes_context=True)
def is_chamber_site(context):
    request = context['request']
    organization = get_current_site(request).user_site.organization
    return isinstance(organization, Chamber)


@register.filter(name='basename')
@stringfilter
def basename(value):
    return os.path.basename(value)


@register.filter
def pop_val(value, key=None):
    if not isinstance(value, (list, OrderedDict)):
        return value

    key = key or list(value.keys())[0]
    return {'name': value.pop(int(key)), 'pk': key}


@register.filter
def basket_quantity(request):
    from centerpokupok.Basket import Basket
    basket = Basket(request)
    return basket.count()


@register.filter
def register_event(instance, event_type_slug):
    """
    Register (save) the Event with defined type slug.
    """
    assert isinstance(instance, models.Model), 'Invalid parameter'
    try:
        content_type = ContentType.objects.get_for_model(instance)
        event_type = RegisteredEventType.objects.get(
            slug=event_type_slug)
    except (RegisteredEventType.DoesNotExist, AttributeError):
        pass
    else:
        return RegisteredEvent.objects.create(
            event_type=event_type,
            content_type=content_type,
            object_id=instance.pk)
    return None


@register.assignment_tag()
def get_length(some_list):
    return length(some_list) \
        if isinstance(some_list, collections.Iterable) else 0


@register.filter
def process_event(event, request):
    """
    Process (define and store attributes values) the Event.
    """
    def _random_ip():
        # For debugging
        import random
        import socket
        import struct
        return socket.inet_ntoa(
            struct.pack('>I', random.randint(1, 0xffffffff)))

    if event:
        assert isinstance(event, RegisteredEvent), 'Invalid parameter'
        event.site = get_current_site(request)
        event.url = request.path
        event.username = request.META.get('REMOTE_USER')
        # event.ip_address = GeoIPHelper.get_request_ip(request)
        event.ip_address = _random_ip()
        event.user_agent = request.META.get('HTTP_USER_AGENT') 
        event.event_hash = event.unique_key
        data = GeoIPHelper.get_geoip_data(event.ip_address) 
        event.event_data = dict((k, str(v)) for k, v in data.items())
        event.is_unique = event.check_is_unique()
        event.save()
    return ''
