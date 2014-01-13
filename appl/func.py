from django.db import models
from core.models import Item
from appl.models import *
from django.contrib.sites.models import get_current_site

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.conf import settings



def getPaginatorRange(page):
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

def getSpecificChildren(cls, parent):
    '''
        Returns not hierarchical children of specific type
            Example: getSpecificChildren("Company", 10)
                //Returns instances of all Companies related with Item=10 by "relation" type of relationship
    '''
    return (globals()[cls]).objects.filter(c2p__parent_id=parent, c2p__type="rel")