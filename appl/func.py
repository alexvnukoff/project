from django.db import models
from core.models import Item
from appl.models import *
from django.contrib.sites.models import get_current_site

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.conf import settings



def getPaginatorRange(page):
    '''
    Method that get page object and return paginotorRange ,
    help to  display properly pagination
    Example
    result = func.getItemsListWithPagination("News", "NAME", "Active_From", "DETAIL_TEXT", "IMAGE", page=4)
    newsList = result[0]
    page = result[1]
    paginator_range = func.getPaginatorRange(page) Pass this object to template

    '''
    if page.number - 2 > 0:
        start = page.number - 2
    else:
        start = 1
    if start + 5 <= page.paginator.num_pages:
        end = start + 5
    else:
        end = page.paginator.num_pages + 1

    paginator_range = range(start, end)
    return paginator_range


def setPaginationForItemsWithValues(items, *attr, page_num=10, page=1):
    '''
    Method  return List of Values of items and  Pagination
    items = Quryset of items
    attr = (list of item's attributes)
    page = number of current page
    page_num = num element per page
    '''
    paginator = Paginator(items, page_num)
    try:
        page = items = paginator.page(page)
    except Exception:
        page = items = paginator.page(1)
    items = tuple([item.pk for item in page.object_list])
    attributeValues = Item.getItemsAttributesValues(attr, items)

    return attributeValues, page #Return List Item and Page object of current page






def getItemsListWithPagination(cls,  *attr,  page=1, site=False):
    '''
    Method  return List of Item of specific class including Pagination
    cls = (class name of specific Item (News , Company))
    attr = (list of item's attributes)
    page = number of current page
    '''
    if site:
        items = (globals()[cls]).objects.filter(sites__id=settings.SITE_ID)
    else:
        items = (globals()[cls]).objects.all()

    paginator = Paginator(items, 10)
    try:
      page = items = paginator.page(page)  #check if page is valid
    except Exception:
      page = items = paginator.page(1)

    items = tuple([item.pk for item in page.object_list])
    attributeValues = (globals()[cls]).getItemsAttributesValues(attr, items)

    return attributeValues, page  #Return List Item and Page object of current page

#TODO: Jenya change func name
def getItemsList(cls,  *attr,  qty=None, site=False):
    '''
    Method  return List of Item of specific class including Pagination
    cls = (class name of specific Item (News , Company))
    attr = (list of item's attributes)
    page = number of current page
    '''
    if site:
        items = (globals()[cls]).objects.filter(sites__id=settings.SITE_ID)[:qty]
    else:
        items = (globals()[cls]).objects.all()[:qty]


    items = tuple([item.pk for item in items])
    attributeValues = (globals()[cls]).getItemsAttributesValues(attr, items)

    return attributeValues
