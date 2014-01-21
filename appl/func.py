from django.db import models
from core.models import *
from appl.models import *
from django.contrib.sites.models import get_current_site
from django.db.models import Count
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

def sortByAttr(cls, attribute, order="ASC", type="str"):#IMPORTANT: should be called before any filter
    '''
        Order Items by attribute
        cls: class name instance of Item
        attribute: Attribute name
        order: Order direction DESC / ASC
        type: Sorting type str/int
            Example: qSet = sortByAtt("Product", "NAME")
            Example: qSet = sortByAtt("Product", "NAME", "DESC", "int")
    '''

    clsObj = (globals()[cls])

    if not issubclass(clsObj, Item):
        raise ValueError("Wrong object type")

    if type != "str":
        case = 'TO_NUMBER("CORE_VALUE"."TITLE", \'999999999.999\')'
    else:
        case = 'CAST("CORE_VALUE"."TITLE" AS VARCHAR(100))'

    if order != "ASC":
        case = '-' + case

    return clsObj.objects.filter(item2value__attr__title=attribute).extra(order_by=[case])

def _setCouponsStructure(couponsDict):

    for item, attrs in couponsDict.items():

        if 'COST' not in attrs or 'COUPON_DISCOUNT' not in attrs:
            raise ValueError('Attributes COST and COUPON_DISCOUNT are required')

        newDict = copy(attrs)

        for attr, values in newDict.items():
            if attr == 'title':
                continue

            if attr == "COUPON_DISCOUNT":
                discount = values[0]

                if not isinstance(discount, dict):
                    raise ValueError('You should pass full attribute data')

                couponsDict[item][attr + '_END_DATE'] = discount['end_date']
                price = float(newDict['COST'][0]['title'])
                couponsDict[item][attr + '_COST'] = price - (price * int(discount['title'])) / 100
                couponsDict[item][attr + '_COST'] = '{0:,.2f}'.format(couponsDict[item][attr + '_COST'])
                couponsDict[item][attr] = discount['title']
            else:
                couponsDict[item][attr] = values[0]['title']

    return couponsDict

def _setProductStructure(prodDict):

    for item, attrs in prodDict.items():

        if 'COST' not in attrs or 'DISCOUNT' not in attrs:
            raise ValueError('Attributes COST and DISCOUNT are required')

        newDict = copy(attrs)

        for attr, values in newDict.items():
            if attr == 'title':
                continue

            if attr == "DISCOUNT":
                discount = values[0]

                price = float(newDict['COST'][0])
                prodDict[item]['DISCOUNT_COST'] = price - (price * float(discount)) / 100
                prodDict[item]['DISCOUNT_COST'] = '{0:,.2f}'.format(prodDict[item]['DISCOUNT_COST'])
                prodDict[item][attr] = discount
            else:
                prodDict[item][attr] = values[0]

    return prodDict


def setStructureForHiearhy(dictinory, items):
    '''
      Method get hierarchy tree and list items with attribute NAME
      and build structure of object
      Example of usage:
       hierarchyStructure = Category.hierarchy.getTree(10)
       categories_id = [cat['ID'] for cat in hierarchyStructure]
       categories = Item.getItemsAttributesValues(("NAME",), categories_id)
       dictStructured = func.setStructureForHiearhy(hierarchyStructure, categories)
       will return :
      {
          {PARENT1}:
                  {PARENT1:item,
                  Child1:item},
           {PARENT2}:
                  {PARENT2:item,
                  Child1:item,
                  Child2:item},
      }


    '''
    level = 0
    dictStructured = {}
    for node in dictinory:
        if node['LEVEL'] == 1:
            i = items[node['ID']]['NAME'][0]
            nameOfList = items[node['ID']]['NAME'][0]
            dictStructured[nameOfList] = {}
            node['item'] = items[node['ID']]
            dictStructured[nameOfList]['Parent'] = node




        else:
            node['pre_level'] = level
            node['item'] = items[node['ID']]
            node['parent_item'] = items[node['PARENT_ID']] if node['PARENT_ID'] is not None else ""
            level = node['LEVEL']
            dictStructured[nameOfList][items[node['ID']]['NAME'][0]] = node

    return dictStructured


def getCountofSepecificRelatedItems(childCls, list, parentCls):
    '''
        Get count of some type of child for list of some type of parents parents
            "childCls" - Type / Class of child objects
            "list" - iterable list of parent ids
            "parentCls" Type / Class of parent objects

                Example: getCountofSepecificRelatedItems("Product", [1, 2], "Category")
                #will return number of products in categories with id 1 and 2

                returns: [{
                    'p2c_parent': 1,
                    'childCount': 4
                }, {
                    'p2c_parent': 2,
                    'childCount': 2
                }]
    '''
    parentObj = (globals()[parentCls])
    clsObj = (globals()[childCls])

    where = '"{0}"."{1}" = "CORE_RELATIONSHIP"."CHILD_ID"'.format(clsObj._meta.db_table, clsObj._meta.pk.column)
    table = '"{0}"'.format(clsObj._meta.db_table)

    return parentObj.objects.filter(p2c__parent_id__in=list, p2c__type="rel", p2c__child_id__isnull=False)\
                                    .values('p2c__parent').annotate(childCount=Count('p2c__parent'))\
                                    .extra(tables=[table], where=[where.upper()])

