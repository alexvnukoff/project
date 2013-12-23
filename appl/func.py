from django.db import models
from core.models import Item
from appl.models import News

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404


def getItemsListWithPagination(cls,  *attr,  page=1):
    '''
    Method  return List of Item of specific class including Pagination
    cls = (class name of specific Item (News , Company))
    attr = (list of item's attributes)
    page = number of current page
    '''
    items = (globals()[cls]).objects.select_related().all()
    paginator = Paginator(items, 2)
    try:
      page = items = paginator.page(page)  #check if page is valid
    except Exception:
      page = items = paginator.page(1)

    itemsList = {}
    for item in items:
        itemsList[item.name] = item.getAttributesValue(*attr)

    return itemsList, page  #Return List Item and Page object of current page

def getItemsList(cls,  *attr,  qny=None):
    '''
    Method return List of Item of specific class
    cls = (class name of specific Item (News , Company))
    attr = (list of item's attributes)
    qny = (number of returned items)
    '''
    items = (globals()[cls]).objects.select_related().all()[:None]
    itemsList = {}
    for item in items:
        itemsList[item.name] = item.getAttributesValue(*attr)
    return itemsList