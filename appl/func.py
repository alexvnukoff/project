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


def setPaginationForItemsWithValues(items, *attr, page_num=10, page=1, fullAttrVal=False):
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
    attributeValues = Item.getItemsAttributesValues(attr, items, fullAttrVal)

    return attributeValues, page #Return List Item and Page object of current page


def getItemsListWithPagination(cls,  *attr,  page=1, site=False):
    '''
    Method  return List of Item of specific class including Pagination
    cls = (class name of specific Item (News , Company))
    attr = (list of item's attributes)
    page = number of current page
    '''

    clsObj = (globals()[cls])

    if not issubclass(clsObj, Item):
        raise ValueError("Wrong object type")

    if site:
        items = clsObj.objects.filter(sites__id=settings.SITE_ID)
    else:
        items = clsObj.objects.all()

    paginator = Paginator(items, 10)
    try:
      page = items = paginator.page(page)  #check if page is valid
    except Exception:
      page = items = paginator.page(1)

    items = tuple([item.pk for item in page.object_list])
    attributeValues = clsObj.getItemsAttributesValues(attr, items)

    return attributeValues, page  #Return List Item and Page object of current page

#TODO: Jenya change func name
def getItemsList(cls,  *attr,  qty=None, site=False, fullAttrVal=False):
    '''
    Method  return List of Item of specific class including Pagination
    cls = (class name of specific Item (News , Company))
    attr = (list of item's attributes)
    page = number of current page
    '''
    clsObj = (globals()[cls])

    if not issubclass(clsObj, Item):
        raise ValueError("Wrong object type")

    if site:
        items = clsObj.objects.filter(sites__id=settings.SITE_ID)[:qty]
    else:
        items = clsObj.objects.all()[:qty]


    items = tuple([item.pk for item in items])
    attributeValues = clsObj.getItemsAttributesValues(attr, items, fullAttrVal=fullAttrVal)

    return attributeValues

def _setCouponsStructure(couponsDict):

    newDict = {}

    for item, attrs in couponsDict.items():

        newDict[item] = {}

        for attr, values in attrs.items():
            if attr == 'title':
                continue

            if attr == "DISCOUNT":
                for discount in values:
                    if discount['end_date']:
                        newDict[item]['DISCOUNT_END_DATE'] = discount['end_date']
                        price = float(couponsDict[item]['COST'][0]['value'])
                        newDict[item]['DISCOUNT_COST'] = price - (price * int(discount['value'])) / 100
                        newDict[item]['DISCOUNT_COST'] = '{0:,.2f}'.format(newDict[item]['DISCOUNT_COST'])
                        newDict[item][attr] = discount['value']
                        break
            else:
                newDict[item][attr] = values[0]['value']

    return newDict