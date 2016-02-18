# -*- encoding: utf-8 -*-

import os
import datetime
import logging
from collections import OrderedDict, Iterable
from copy import copy
from decimal import Decimal
from urllib.parse import urljoin

from django.db.models import Q
from django.conf import settings
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
from guardian.shortcuts import get_objects_for_user

from appl.func import currency_symbol
from b24online.models import (Chamber, Notification, RegisteredEventType,
                              RegisteredEvent, MessageChat, Message)
from b24online.stats.helpers import RegisteredEventHelper
from b24online.utils import resize

from tpp.SiteUrlMiddleWare import get_request
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


@register.filter(name='remove_whitespaces')
def remove_whitespaces(sentence):
    return " ".join(sentence.split())


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
    """
    Return the number od unread messages.
    """
    request = context.get('request')
    if request.user.is_authenticated():
        message = Message.objects.select_related('chat')\
            .filter(chat__participants__id__exact=request.user.id,
                    chat__status=MessageChat.OPENED,
                    is_read=False)\
            .filter(~Q(sender=request.user))\
            .distinct()\
            .count()
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


@register.assignment_tag()
def get_length(some_list):
    """
    Return the length of some iterable
    """
    return len(some_list) \
        if isinstance(some_list, Iterable) else 0


### FIXME: (andrey_k) delete it ###
@register.filter()
def to_list(some_dict):
    return [(k, v) for k, v in some_dict.items()]


@register.filter()
def show_type(instance):
    return type(instance)
### -- ###    


@register.filter
def register_event(instance, event_type_slug):
    """
    Register (save) the Event with defined type slug.
    """
    return RegisteredEventHelper.get_stored_event(instance, event_type_slug)


@register.filter
def process_event(event_stored_data, request):
    """
    Register the event (define and store attributes values).
    Return empty string.
    """
    RegisteredEventHelper.register(event_stored_data, request)
    return ''


@register.filter
def deal_order_quantity(request):
    """
    Return the draft deal orders count.
    """
    from b24online.models import (Organization, DealOrder, Deal, DealItem)

    if request.user.is_authenticated():
        org_ids = get_objects_for_user(
            request.user, ['b24online.manage_organization'],
            Organization.get_active_objects().all(), 
            with_superuser=False)
        return DealItem.objects.select_related('deal', 'deal__deal_order')\
            .filter(
                ~Q(deal__status__in=[Deal.PAID, Deal.ORDERED]) & \
            ((Q(deal__deal_order__customer_type=DealOrder.AS_PERSON) & \
                Q(deal__deal_order__created_by=request.user)) | \
            (Q(deal__deal_order__customer_type=DealOrder.AS_ORGANIZATION) & \
                Q(deal__deal_order__customer_organization_id__in=org_ids))))\
            .count()
    else:
        return None


@register.filter
def deal_quantity(request):
    """
    Return the paid deals count.
    """
    from b24online.models import Deal
    return Deal.get_user_deals(request.user, status=Deal.PAID)\
        .count() if request.user.is_authenticated() else 0


@register.filter
def get_by_content_type(item):
    """
    Return model instance by content_type and object_id.
    """
    content_type_id = item.get('content_type_id')
    instance_id = item.get('object_id')
    if content_type_id and instance_id:        
        try:
            content_type = ContentType.objects.get(pk=content_type_id)
        except ContentType.DoesNotExist:
            pass
        else:
            model_class = content_type.model_class()
            try:
                return model_class.objects.get(pk=instance_id)
            except model_class.DoesNotExist:
                pass
    return None


@register.filter
def thumbnail(img, param_str):
    """
    Make and return the path to image thumbnail.
    """
    img_url = str(img)
    try:
        sizes, cropped = param_str.split('_')
    except ValueError:
        pass
    else:
        try:
            size_px, size_py = list(map(int, sizes.split('x')))
            cropped = bool(int(cropped))
        except ValueError:
            pass
        else:
            try:
                _path, _filename = os.path.split(img_url)    
                _file, _ext = _filename.split('.')
            except ValueError:
                pass
            else:
                thumbnail_name = r'%s__%s.%s' % (_file, param_str, _ext)
                thumbnail_path = os.path.join(
                    settings.MEDIA_ROOT, 
                    'thumbnails',
                    _path, 
                    thumbnail_name
                )
                thumbnail_url = urljoin('thumbnails/', _path + '/') + thumbnail_name
                sized_image_path = os.path.join(settings.MEDIA_ROOT, thumbnail_path)
                image_path = os.path.join(settings.MEDIA_ROOT, img_url)
                if not os.path.exists(sized_image_path) and \
                    os.path.exists(image_path):
                    directory = os.path.dirname(sized_image_path)
                    if not os.path.exists(directory):
                        try:
                            os.makedirs(directory)
                        except OSError as e:
                            if e.errno != errno.EEXIST:
                                raise
                    resize(image_path, (size_px, size_px), cropped, sized_image_path) 
                return urljoin(settings.MEDIA_URL, thumbnail_url)
    return urljoin(settings.MEDIA_URL, img_url)


@register.filter
def mark_as_read(message):
    """
    Make a message as read.
    """
    assert isinstance(message, Message), \
        _('Invalid parameter. Must be :class:`Message`')
    if message.pk:
        message.is_read = True
        message.save()
    return ''


@register.assignment_tag(takes_context=True)
def get_chat_other_side(context, chat):
    """
    Return the chat's 'other side'.
    """
    request = context['request']
    if request.user.is_authenticated():
        if chat.created_by == request.user:
            return chat.recipient
        else:
            return chat.created_by
    return None
