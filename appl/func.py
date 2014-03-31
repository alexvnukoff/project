from core.models import *
from appl.models import *
from django.db.models import Count, F
from django.core.paginator import Paginator
from django.conf import settings
from PIL import Image
from django.template import RequestContext, loader
from django.utils.translation import ugettext as _
from haystack.query import SearchQuerySet, SQ
import lxml
from lxml.html.clean import clean_html
from django.core.cache import cache
def getPaginatorRange(page):
    '''
    Method that get page object and return paginatorRange ,
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


def setPaginationForSearchWithValues(items, *attr, page_num=10, page=1, fullAttrVal=False):
    '''
    Method  return List of Values of items and  Pagination
    items = QuerySet of items
    attr = (list of item's attributes)
    page = number of current page
    page_num = num element per page
    '''
    paginator = Paginator(items, page_num)
    try:
        page = items = paginator.page(page)
    except Exception:
        page = items = paginator.page(1)
    if not isinstance(items, list):
        items = tuple([item.id for item in page.object_list])
    attributeValues = Item.getItemsAttributesValues(attr, items, fullAttrVal)

    return attributeValues, page #Return List Item and Page object of current page

def setPaginationForItemsWithValues(items, *attr, page_num=10, page=1, fullAttrVal=False):
    '''
    Method  return List of Values of items and  Pagination
    items = QuerySet of items
    attr = (list of item's attributes)
    page = number of current page
    page_num = num element per page
    '''
    paginator = Paginator(items, page_num)
    try:
        page = items = paginator.page(page)
    except Exception:
        page = items = paginator.page(1)
    if not isinstance(items, list):
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
        items = clsObj.active.get_active().filter(sites__id=settings.SITE_ID)
    else:
        items = clsObj.active.get_active().all()

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

        items = clsObj.active.get_active().filter(sites__id=settings.SITE_ID)[:qty]
    else:
        items = clsObj.active.get_active().all()[:qty]


    items = tuple([item.pk for item in items])
    attributeValues = clsObj.getItemsAttributesValues(attr, items, fullAttrVal=fullAttrVal)

    return attributeValues

#Deprecated
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

    return clsObj.active.get_active().filter(item2value__attr__title=attribute).extra(order_by=[case])

def sortQuerySetByAttr(queryset, attribute, order="ASC", type="str"):#IMPORTANT: should be called before any filter
    '''
        Order Items by attribute
        cls: class name instance of Item
        attribute: Attribute name
        order: Order direction DESC / ASC
        type: Sorting type str/int
            Example: qSet = sortByAtt("Product", "NAME")
            Example: qSet = sortByAtt("Product", "NAME", "DESC", "int")
    '''

    if type != "str":
        case = 'TO_NUMBER("CORE_VALUE"."TITLE", \'999999999.999\')'
    else:
        case = 'CAST("CORE_VALUE"."TITLE" AS VARCHAR(100))'

    if order != "ASC":
        case = '-' + case

    return queryset.model.objects.filter(pk__in=queryset, item2value__attr__title=attribute).extra(order_by=[case])

def currencySymbol(currency):
    symbols = {
        'EUR': '€',
        'USD': '$',
        'NIS': '₪',
    }

    return symbols.get(currency.upper(), currency)

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
                couponsDict[item][attr] = discount['title']
            else:
                couponsDict[item][attr] = values[0]['title']

    return couponsDict

#Deprecated
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
                prodDict[item]['COST_DIFFERENCE'] = price - prodDict[item]['DISCOUNT_COST']
                prodDict[item]['COST_DIFFERENCE'] = '{0:,.0f}'.format(prodDict[item]['COST_DIFFERENCE'])
                prodDict[item]['DISCOUNT_COST'] = '{0:,.2f}'.format(prodDict[item]['DISCOUNT_COST'])
                prodDict[item][attr] = discount
            elif attr == "COST":
                prodDict[item]['COST'] = '{0:,.2f}'.format(float(newDict['COST'][0]))
            elif attr == "CURRENCY":
                prodDict[item][attr] = values[0]['title']
                prodDict[item][attr + '_SYMBOL'] = currencySymbol(prodDict[item][attr])
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
    #TODO: Parent not always be first because of sorting
    for node in dictinory:
        if node['LEVEL'] == 1:
            nameOfList = items[node['ID']]['NAME'][0].strip()
            dictStructured[nameOfList] = {}
            node['item'] = items[node['ID']]
            dictStructured[nameOfList]['@Parent'] = node
        else:
            node['pre_level'] = level
            node['item'] = items[node['ID']]
            node['parent_item'] = items[node['PARENT_ID']] if node['PARENT_ID'] is not None else ""
            level = node['LEVEL']
            dictStructured[nameOfList][items[node['ID']]['NAME'][0].strip()] = node

    return dictStructured


def getCountofSepecificItemsRelated(childCls, list, filterChild = None):
    '''
        Get count of some type of child for list of some type of parents parents
            "childCls" - Type / Class of child objects
            "list" - iterable list of parent ids

                Example: getCountofSepecificRelatedItems("Product", [1, 2], "Category")
                #will return number of products in categories with id 1 and 2

                returns: [{
                    'parent': 1,
                    'childCount': 4
                }, {
                    'parent': 2,
                    'childCount': 2
                }]
    '''
    clsObj = (globals()[childCls])

    if filterChild is None:
        filterChild = F(clsObj._meta.model_name)

    return Item.objects.filter(c2p__parent_id__in=list, c2p__child_id=filterChild, c2p__type="relation")\
                                .values('c2p__parent').annotate(childCount=Count('c2p__parent'))

def _categoryStructure(categories,  listCount, catWithAttr, needed=None):

    elCount = {}
    parent = 0

    if len(listCount) == 0:
        return {}

    keys = list(listCount[0].keys())
    childKey = 'childCount'

    parentKey = keys[1]

    if childKey == parentKey:
        parentKey = keys[0]

    if needed is not None:
        for cat in catWithAttr:
            if cat not in needed:
                del catWithAttr[cat]

    for dictCount in listCount:
        elCount[dictCount[parentKey]] = dictCount[childKey]


    for cat in categories:

        if cat['LEVEL'] == categories[0]['LEVEL']:
            parent = cat['ID']

        if 'count' not in catWithAttr[parent]:
            catWithAttr[parent]['count'] = elCount.get(cat['ID'], 0)
        else:
            catWithAttr[parent]['count'] += elCount.get(cat['ID'], 0)

    return catWithAttr


def resize(img, box, fit, out):
        '''Downsample the image.
        @param img: Image -  an Image-object
        @param box: tuple(x, y) - the bounding box of the result image
        @param fit: boolean - crop the image to fill the box
        @param out: file-like-object - save the image into the output stream
        '''
        #preresize image with factor 2, 4, 8 and fast algorithm

        img = Image.open(img)

        factor = 1
        while img.size[0]/factor > 2*box[0] and img.size[1]/factor > 2*box[1]:
            factor *=2
        if factor > 1:
            img.thumbnail((img.size[0]/factor, img.size[1]/factor), Image.NEAREST)

        #calculate the cropping box and get the cropped part
        if fit:
            x1 = y1 = 0
            x2, y2 = img.size
            wRatio = 1.0 * x2/box[0]
            hRatio = 1.0 * y2/box[1]
            if hRatio > wRatio:
                y1 = int(y2/2-box[1]*wRatio/2)
                y2 = int(y2/2+box[1]*wRatio/2)
            else:
                x1 = int(x2/2-box[0]*hRatio/2)
                x2 = int(x2/2+box[0]*hRatio/2)
            img = img.crop((x1,y1,x2,y2))

        #Resize the image with best quality algorithm ANTI-ALIAS
        img.thumbnail(box, Image.ANTIALIAS)

        #if img.mode != "RGB":
        #    img = img.convert("RGB")

        #save it into a file-like object
        img.save(out, "PNG", quality=95)




def findKeywords(tosearch):
    import string
    import difflib

    exclude = set(string.punctuation)
    exclude.remove('-')
    tosearch = ''.join(ch for ch in tosearch if ch not in exclude and (ch.strip() != '' or ch == ' '))
    words = [word.lower() for word in tosearch.split(" ") if 3 <= len(word) <= 20 and word.isdigit() is False][:30]

    length = len(words)
    keywords = []

    for word in words:
        if len(difflib.get_close_matches(word, keywords)) > 0:
            continue

        count = len(difflib.get_close_matches(word, words))

        precent = (count * length) / 100

        if 2.5 <= precent <= 3:
            keywords.append(word)

        if len(keywords) > 5:
            break

    if len(keywords) < 3:
        for word in words:
            if len(difflib.get_close_matches(word, keywords)) == 0:
                keywords.append(word)

                if len(keywords) == 3:
                    break

    return ' '.join(keywords)


def notify(message_type, notificationtype, **params):
    user = params['user']
    params['user'] = user.pk
    message = SystemMessages.objects.get(type=message_type)
    notif = Notification(user=user, message=message, create_user=user)
    notif.save()


    sendTask(notificationtype, **params)


def sendTask(type, **params):
    import redis
    from django.conf import settings
    import json
    from django.http import HttpResponse

    ORDERS_FREE_LOCK_TIME = getattr(settings, 'ORDERS_FREE_LOCK_TIME', 0)
    ORDERS_REDIS_HOST = getattr(settings, 'ORDERS_REDIS_HOST', 'localhost')
    ORDERS_REDIS_PORT = getattr(settings, 'ORDERS_REDIS_PORT', 6379)
    ORDERS_REDIS_PASSWORD = getattr(settings, 'ORDERS_REDIS_PASSWORD', None)
    ORDERS_REDIS_DB = getattr(settings, 'ORDERS_REDIS_DB', 0)

    # опять удобства
    service_queue = redis.StrictRedis(
        host=ORDERS_REDIS_HOST,
        port=ORDERS_REDIS_PORT,
        db=ORDERS_REDIS_DB,
        password=ORDERS_REDIS_PASSWORD
    ).publish

    service_queue(type, json.dumps(params))


def getAnalytic(params = None):

    from appl.analytic.analytic import get_results

    if not isinstance(params, dict):
        raise ValueError('Filter required')

    if 'end_date' not in params:
        params['end_date'] = '2050-01-01'
    if 'start_date' not in params:
        params['start_date'] = '2014-01-01'

    params['metrics'] = 'ga:visitors'

    return get_results(**params)



def addDictinoryWithCountryAndOrganization(ids, itemList):

    countries = Country.objects.filter(p2c__child__in=Organization.objects.all(), p2c__child__p2c__child__in=ids,
                                       p2c__child__p2c__type='dependence').values('p2c__child__p2c__child', 'pk')

    countries_id = [country['pk'] for country in countries]
    countriesList = Item.getItemsAttributesValues(("NAME", 'FLAG'), countries_id)

    organizations = Organization.objects.filter(p2c__child__in=ids, p2c__type='dependence').values('p2c__child', 'pk')
    organizations_ids = [organization['pk'] for organization in organizations]
    organizationsList = Item.getItemsAttributesValues(("NAME", 'FLAG', 'SLUG'), organizations_ids)
    organizations_dict = {}
    for organization in organizations:
        organizations_dict[organization['p2c__child']] = organization['pk']


    country_dict = {}
    for country in countries:
        country_dict[country['p2c__child__p2c__child']] = country['pk']

    for id, item in itemList.items():
        if country_dict.get(id, False):
            toUpdate = {'COUNTRY_NAME': countriesList[country_dict[id]].get('NAME', [0]) if country_dict.get(id, [0]) else [0],
                        'COUNTRY_FLAG': countriesList[country_dict[id]].get('FLAG', [0]) if country_dict.get(id, [0]) else [0],
                        'COUNTRY_ID':  country_dict.get(id, 0)}
            item.update(toUpdate)
        if organizations_dict.get(id, False):
            if organizationIsCompany(id):
                url = 'companies:detail'
            else:
                url = 'tpp:detail'

            toUpdate = {'ORGANIZATION_FLAG': organizationsList[organizations_dict[id]].get('FLAG', [0]) if organizations_dict.get(id, [0]) else [0],
                        'ORGANIZATION_NAME': organizationsList[organizations_dict[id]].get('NAME', [0]) if organizations_dict.get(id, [0]) else [0],
                        'ORGANIZATION_SLUG': organizationsList[organizations_dict[id]].get('SLUG', [0]) if organizations_dict.get(id, [0]) else [0],
                        'ORGANIZATION_ID': organizations_dict.get(id, 0),
                        'ORGANIZATION_URL': url}
            item.update(toUpdate)




def addDictinoryWithCountryAndOrganizationToInnov(ids, itemList):

        cabinets = Cabinet.objects.filter(p2c__child__in=ids,).values('p2c__child', 'pk')

        cabinets_ids = [cabinet['pk'] for cabinet in cabinets]
        countries = Country.objects.filter(p2c__child__in=cabinets_ids).values('p2c__child', 'pk')

        countries_id = [country['pk'] for country in countries]
        countriesList = Item.getItemsAttributesValues(("NAME", 'FLAG'), countries_id)

        country_dict = {}

        for country in countries:
            if country['pk']:
               country_dict[country['p2c__child']] = country['pk']

        cabinetList = Item.getItemsAttributesValues(("USER_FIRST_NAME", 'USER_LAST_NAME'), cabinets_ids)

        cabinets_dict = {}

        for cabinet in cabinets:
            cabinets_dict[cabinet['p2c__child']] = {
                'CABINET_NAME': cabinetList[cabinet['pk']].get('USER_FIRST_NAME', 0) if cabinetList.get(cabinet['pk'], 0) else [0],
                'CABINET_LAST_NAME': cabinetList[cabinet['pk']].get('USER_LAST_NAME', 0) if cabinetList.get(cabinet['pk'], 0) else [0],
                'CABINET_ID': cabinet['pk'],
                'CABINET_COUNTRY_NAME': countriesList[country_dict[cabinet['pk']]].get('NAME', [0]) if country_dict.get(cabinet['pk'], False) else [0],
                'CABINET_COUNTRY_FLAG': countriesList[country_dict[cabinet['pk']]].get('FLAG', [0]) if country_dict.get(cabinet['pk'], False) else [0],
                'CABINET_COUNTRY_ID': country_dict.get(cabinet['pk'], "")
            }

        addDictinoryWithCountryAndOrganization(ids, itemList)


        for id, innov in itemList.items():
            if cabinets_dict.get(id, 0):
                innov.update(cabinets_dict.get(id, 0))



def addDictinoryWithCountryToCompany(ids, itemList):

        countries = Country.objects.filter(p2c__child__in=ids, p2c__type='dependence').values('p2c__child', 'pk')
        countries_id = [country['pk'] for country in countries]
        countriesList = Item.getItemsAttributesValues(("NAME", 'FLAG'), countries_id)
        country_dict = {}

        for country in countries:
            country_dict[country['p2c__child']] = country['pk']

        for id, company in itemList.items():
            toUpdate = {'COUNTRY_NAME': countriesList[country_dict[id]].get('NAME', [0]) if country_dict.get(id, 0) else [0],
                        'COUNTRY_FLAG': countriesList[country_dict[id]].get('FLAG', [0]) if country_dict.get(id, 0) else [0],
                        'COUNTRY_ID':  country_dict.get(id, 0)}
            company.update(toUpdate)





def addToItemDictinoryWithCountryAndOrganization(id, itemList, withContacts=False):

    countries = Country.objects.filter(p2c__child__in=Organization.objects.all(), p2c__child__p2c__type='dependence',
                                       p2c__child__p2c__child=id).values('p2c__child__p2c__child', 'pk')

    countries_id = [country['pk'] for country in countries]
    countriesList = Item.getItemsAttributesValues(("NAME", 'FLAG'), countries_id)

    organizations = Organization.objects.filter(p2c__child=id, p2c__type='dependence').values('p2c__child', 'pk')
    organizations_ids = [organization['pk'] for organization in organizations]
    attr = ("NAME", 'FLAG', 'IMAGE', 'SLUG')

    if withContacts:
        attr = attr + ('EMAIL', 'SITE_NAME', 'ADDRESS', 'TELEPHONE_NUMBER', 'FAX')
    organizationsList = Item.getItemsAttributesValues(attr, organizations_ids)
    organizations_dict = {}
    for organization in organizations:
        organizations_dict[organization['p2c__child']] = organization['pk']


    country_dict = {}
    for country in countries:
        country_dict[country['p2c__child__p2c__child']] = country['pk']


    if country_dict.get(id, False):
            toUpdate = {'COUNTRY_NAME': countriesList[country_dict[id]].get('NAME', 0) if country_dict.get(id, 0) else [0],
                        'COUNTRY_FLAG': countriesList[country_dict[id]].get('FLAG', 0) if country_dict.get(id, 0) else [0],
                        'COUNTRY_ID':  country_dict.get(id, 0)}
            itemList.update(toUpdate)
    if organizations_dict.get(id, False):
            if organizationIsCompany(id):
                url = 'companies:detail'
            else:
                url = 'tpp:detail'
            toUpdate = {'ORGANIZATION_FLAG': organizationsList[organizations_dict[id]].get('FLAG', 0) if organizations_dict.get(id, 0) else [0],
                        'ORGANIZATION_NAME': organizationsList[organizations_dict[id]].get('NAME', 0) if organizations_dict.get(id, 0) else [0],
                        'ORGANIZATION_IMAGE': organizationsList[organizations_dict[id]].get('IMAGE', 0) if organizations_dict.get(id, 0) else [0],
                        'ORGANIZATION_SLUG': organizationsList[organizations_dict[id]].get('SLUG', [0]) if organizations_dict.get(id, [0]) else [0],
                        'ORGANIZATION_EMAIL': organizationsList[organizations_dict[id]].get('EMAIL', [""]) if organizations_dict.get(id, [0]) else [0],
                        'ORGANIZATION_SITE_NAME': organizationsList[organizations_dict[id]].get('SITE_NAME', [""]) if organizations_dict.get(id, [0]) else [0],
                        'ORGANIZATION_ADDRESS': organizationsList[organizations_dict[id]].get('ADDRESS', [""]) if organizations_dict.get(id, [0]) else [0],
                        'ORGANIZATION_TELEPHONE_NUMBER': organizationsList[organizations_dict[id]].get('FAX', [""]) if organizations_dict.get(id, [0]) else [0],
                        'ORGANIZATION_FAX': organizationsList[organizations_dict[id]].get('FAX', [""]) if organizations_dict.get(id, [0]) else [0],
                        'ORGANIZATION_ID': organizations_dict.get(id, 0),
                        'ORGANIZATION_URL': url}
            itemList.update(toUpdate)


def organizationIsCompany(item_id):
    if Company.objects.filter(p2c__child=item_id, p2c__type='dependence').exists():
        return True
    return False

def filterLive(request):

    searchFilter = []
    filtersIDs = {}
    filters = {}
    ids = []

    filterList = ['tpp', 'country', 'branch']

    for name in filterList:
        filtersIDs[name] = []
        filters[name] = []

        for pk in request.GET.getlist('filter[' + name + '][]', []):
            try:
                filtersIDs[name].append(int(pk))
            except ValueError:
                continue

        ids += filtersIDs[name]


    if len(ids) > 0:
        attributes = Item.getItemsAttributesValues('NAME', ids)

        for pk, attr in attributes.items():

            if not isinstance(attr, dict) or 'NAME' not in attr or len(attr['NAME']) != 1:
                continue

            for name, id in filtersIDs.items():

                if pk in id:
                    filters[name].append({'id': pk, 'text': attr['NAME'][0]})

                newIDs = []
                #Security
                for i in id:
                    try:
                        newIDs.append(str(int(i)))
                    except ValueError:
                        continue

                if len(newIDs) > 0:
                    searchFilter.append('SQ(' + name + '__in =[' + ','.join(newIDs) + '])')

    if len(searchFilter) > 0:
        searchFilter = eval(' | '.join(searchFilter))

    return filters, searchFilter


def getB2BcabinetValues(request):
    if request.user.is_authenticated():
        user = request.user
        current_company = request.session.get('current_company', False)
        if current_company:
           current_company = Organization.objects.get(pk=current_company).getAttributeValues("NAME")
        cabinet = Cabinet.objects.get(user=user.pk)

        try:
            country = Country.objects.get(p2c__child=cabinet)
            country = country.getAttributeValues('NAME')
        except Exception:
            country = ""
        cabinetValues = {}
        cabinetValues['EMAIL'] = [user.email]
        cabinetValues['LOGIN'] = [user.username]
        cabinetValues.update(cabinet.getAttributeValues('PROFESSION', 'MOBILE_NUMBER', 'BIRTHDAY', 'PERSONAL_STATUS', 'SEX',
                                                'SKYPE', 'SITE_NAME', 'ICQ', 'USER_MIDDLE_NAME', 'USER_FIRST_NAME',
                                                'USER_LAST_NAME', 'IMAGE', 'TELEPHONE_NUMBER'))
        cabinetValues['COUNTRY'] = country
        cabinetValues['CURRENT_COMPANY'] = current_company if current_company else ['']


        return cabinetValues

    return None

def getBanners(places, site, filterAdv=None):

    bList = []

    for place in places:
        banner = AdvBanner.active.get_active().filter(c2p__parent__title=place, c2p__type="relation", sites=site)

        if filterAdv is not None and len(filterAdv) > 0:
            banner = banner.filter(c2p__parent__in=filterAdv, c2p__type='relation')

        banner = banner.order_by('?').values_list('pk', flat=True)[:1]

        if len(banner) == 1:
            bList.append(banner[0])

    bAttr = Item.getItemsAttributesValues(('NAME', 'SITE_NAME', 'IMAGE'), bList)

    return bAttr

def getTops(request, filterAdv=None):

    models = {
        Product: {
            'count': 5,
            'text': _('Products'),
            'detailUrl': 'products:detail'
        },
        InnovationProject: {
            'count': 5,
            'text': _('Innovation Projects'),
            'detailUrl': 'innov:detail'
        },
        Company: {
            'count': 5,
            'text': _('Companies'),
            'detailUrl': 'companies:detail'
        },
        BusinessProposal: {
            'count': 5,
            'text': _('Business Proposals'),
            'detailUrl': 'proposal:detail'
        },
    }

    topList = []
    modelTop = {}

    for model, modelDict in models.items():

        sub = model.objects.all()
        top = AdvTop.active.get_active().filter(c2p__parent=sub, c2p__type="dependence").values_list('c2p__parent', flat=True)

        if filterAdv is not None and len(filterAdv) > 0:
            top = top.filter(c2p__parent__in=filterAdv, c2p__type='relation')

        top = top.order_by('?')[:int(modelDict['count'])]

        tops = list(top)

        sModel = model.__name__

        if len(tops) > 0:
            topList += tops
            modelTop[sModel] = tops


    topAttr = Item.getItemsAttributesValues(('NAME', 'DETAIL_TEXT', 'IMAGE', 'SLUG'), topList)

    tops = {}

    for id, attrs in topAttr.items():

        if not isinstance(attrs, dict):
            continue

        for model in models:


            sModel = model.__name__

            if sModel not in modelTop:
                continue


            if sModel not in tops:
                tops[sModel] = {}
                tops[sModel]['MODEL'] = models[model]
                tops[sModel]['elements'] = {}
                tops[sModel]['ids'] = []

            if id in modelTop[sModel]:
                tops[sModel]['elements'][id] = attrs
                tops[sModel]['ids'].append(id)

                break

    for name, attr in tops.items():
       if name == BusinessProposal.__name__ or Product.__name__ == name:
           addDictinoryWithCountryAndOrganization(attr['ids'], attr['elements'])
       if name == InnovationProject.__name__:
           addDictinoryWithCountryAndOrganizationToInnov(attr['ids'], attr['elements'])
       if name == Company.__name__:
           addDictinoryWithCountryToCompany(attr['ids'], attr['elements'])



    return tops

def getDeatailAdv(item_id):


    filterAdv = []
    sqs = getActiveSQS().filter(id=item_id)


    filterAdv += getattr(sqs, 'branch', [])
    filterAdv += getattr(sqs, 'tpp', [])

    if len(filterAdv) == 0:
        filterAdv.append(item_id)

    return filterAdv

def getListAdv(request):
    filtersAdv = []

    filterList = ['tpp', 'country', 'branch']


    for name in filterList:

        ids = []

        for pk in request.GET.getlist('filter[' + name + '][]', []):
            try:
                ids.append(int(pk))
            except ValueError:
                continue

        if name != 'tpp':
            filtersAdv += ids
        else:
            sqs = getActiveSQS().models(Tpp)

            if len(ids) > 0:
                sqs = sqs.filter(django_id__in=ids)


            for tpp in sqs:
                if len(tpp.country) > 0:
                    filtersAdv += tpp.country

    return filtersAdv


def getActiveSQS():
    return SearchQuerySet().filter(SQ(obj_end_date__gt=timezone.now())| SQ(obj_end_date__exact=datetime.datetime(1 , 1, 1)),
                                                               obj_start_date__lt=timezone.now())
def emptyCompany():
     template = loader.get_template('permissionDen.html')
     request = get_request()
     context = RequestContext(request, {})
     page = template.render(context)
     return page

def permissionDenied():
     template = loader.get_template('permissionDenied.html')
     request = get_request()
     context = RequestContext(request, {})
     page = template.render(context)
     return page

def setContent(request, model, attr, url, template_page, page_num, page=1, my=None):

    cached = False
    cache_name = "%s_list_result_page_%s" % (model.__name__, page)
    query = request.GET.urlencode()

    if not my and not request.user.is_authenticated():
        if query.find('sortField') == -1 and query.find('order') == -1 and query.find('filter') == -1:
            cached = cache.get(cache_name)

    if not cached:

        q = request.GET.get('q', '')

        if not my:
            filters, searchFilter = filterLive(request)

            sqs = getActiveSQS().models(model)
            if model is News:
               sqs = sqs.filter(categories__gt=0)

            if len(searchFilter) > 0: #Got filter values
                sqs = sqs.filter(searchFilter)

            if q != '': #Search for content
                sqs = sqs.filter(SQ(title=q) | SQ(text=q))

            sortFields = {
                'date': 'id',
                'name': 'title'
            }

            order = []

            sortField1 = request.GET.get('sortField1', 'date')
            sortField2 = request.GET.get('sortField2', None)
            order1 = request.GET.get('order1', 'desc')
            order2 = request.GET.get('order2', None)

            if sortField1 and sortField1 in sortFields:
                if order1 == 'desc':
                    order.append('-' + sortFields[sortField1])
                else:
                    order.append(sortFields[sortField1])
            else:
                order.append('-id')

            if sortField2 and sortField2 in sortFields:
                if order2 == 'desc':
                    order.append('-' + sortFields[sortField2])
                else:
                    order.append(sortFields[sortField2])

            proposal = sqs.order_by(*order)
            url_paginator = "%s:paginator" % (url)

            params = {
                'filters': filters,
                'sortField1': sortField1,
                'sortField2': sortField2,
                'order1': order1,
                'order2': order2
            }

        else:
            current_organization = request.session.get('current_company', False)

            if current_organization:
                if model != Tpp:
                    proposal = getActiveSQS().models(model).\
                        filter(SQ(tpp=current_organization) | SQ(company=current_organization))
                else:
                    proposal = getActiveSQS().models(model).\
                        filter(SQ(id=current_organization) | SQ(company=current_organization))


                if q != '': #Search for content
                    proposal = proposal.filter(SQ(title=q) | SQ(text=q))

                proposal.order_by('-obj_create_date')

                url_paginator = "%s:my_main_paginator" % url
                params = {}
            else:
                 raise ObjectDoesNotExist('you need check company')


        result = setPaginationForSearchWithValues(proposal, *attr, page_num=page_num, page=page)

        proposalList = result[0]
        proposal_ids = [id for id in proposalList.keys()]
        redactor = False
        if request.user.is_authenticated():
            items_perms = getUserPermsForObjectsList(request.user, proposal_ids, model.__name__)
        else:
            items_perms = ""
        if model is News or model is TppTV:
            if 'Redactor' in request.user.groups.values_list('name', flat=True):
                 redactor = True




        addDictinoryWithCountryAndOrganization(proposal_ids, proposalList)

        page = result[1]
        paginator_range = getPaginatorRange(page)




        template = loader.get_template(template_page)

        templateParams = {
            'proposalList': proposalList,
            'page': page,
            'paginator_range': paginator_range,
            'url_paginator': url_paginator,
            'items_perms': items_perms,
            'current_path': request.get_full_path(),
            'redactor': redactor

        }
        templateParams.update(params)

        context = RequestContext(request, templateParams)
        rendered = template.render(context)

        if not my and not request.user.is_authenticated():
            if query.find('sortField') == -1 and query.find('order') == -1 and query.find('filter') == -1:
                cache.set(cache_name, rendered)

    else:
        rendered = cache.get(cache_name)
    return rendered





def cleanFromHtml(value):

    if len(value) > 0:
        document = lxml.html.document_fromstring(value)
        raw_text = document.text_content()
        return raw_text
    else:
        return  ""

def getUserPermsForObjectsList(user, obj_lst, obj_model_name):
    '''
        Receive User, list of Items PK obj_lst and model name of these Items obj_model_name, for example, "Product".
        Returns dictionary with list of permissions for current user for each object instance.
        Example:    user = User.objects.get(pk=1)
                    getUserPermsForObjectsList(user, [1, 2, 34, 67], 'Product')
        Return:
        {
            '1': ['add_product', 'change_product', 'read_product', 'delete_product'],
            '2': ['add_product', 'read_product'],
            '34': ['read_product'],
            '67': ['add_product', 'change_product', 'read_product', 'delete_product']
        }
    '''
    if len(obj_lst) == 0:
        return {}

    perms_dict = {}
    items = (globals()[obj_model_name]).objects.filter(pk__in=obj_lst)

    for itm in items:
        perms_dict[str(itm.pk)] = itm.getItemInstPermList(user)

    return perms_dict
