from django.db import models
from core.models import Item
from django.contrib.sites.models import get_current_site

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.conf import settings


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