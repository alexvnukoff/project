__author__ = 'user'
from django.shortcuts import render_to_response
from appl import func
from appl.models import Product, Category
from django.template import RequestContext
from django.utils.timezone import now
from datetime import timedelta

def couponsList(request, currentCat = None):
    page = request.GET.get('page', 1)
    sort = request.GET.get('sort', 'ed-date')
    order = request.GET.get('order', 'ASC')
    expire = request.GET.get('expire', None)
    orderSymb = ''

    if currentCat == None:#not filtered list

        #Getting related categories
        categories = Category.hierarchy.getTree(15)
        category_root_ids = [cat['ID'] for cat in categories if cat['LEVEL'] == 1]

        breadCrumbs = None
    else:
        #Getting related categories
        currentCat = int(currentCat)
        categories = Category.hierarchy.getDescendants(currentCat)
        category_root_ids = [cat['ID'] for cat in categories if cat['LEVEL'] == 2][:15]

        #creating bread crumbs
        ancestors = Category.hierarchy.getAncestors(currentCat)
        ancestors_ids = [cat['ID'] for cat in ancestors]
        breadCrumbs = Product.getItemsAttributesValues(("NAME",), ancestors_ids)


    category_ids = [cat['ID'] for cat in categories]

    #sort categories
    rootCats = Category.objects.filter(pk__in=category_root_ids)
    sortedRootCat = func.sortQuerySetByAttr(rootCats, "NAME", "ASC", "str")

    category_root_ids = [cat.pk for cat in sortedRootCat]

    if currentCat is not None:
        category_root_ids.insert(0, currentCat)

    couponsObj = Product.getCoupons()

    if expire is not None:
        expire = int(expire)
        time = now() + timedelta(days=expire)
        couponsObj = couponsObj.filter(item2value__end_date__lte=time)


    prodInCat = func.getCountofSepecificItemsRelated('Product', category_ids, couponsObj)
    categoriesWithAttr = Product.getItemsAttributesValues(("NAME",), category_root_ids)

    if currentCat is not None:
        currentCatName = categoriesWithAttr[currentCat]['NAME'][0]
        category_ids.append(currentCat)
        del categoriesWithAttr[currentCat]
    else:
        currentCatName = None

    categories = func._categoryStructure(categories, prodInCat, categoriesWithAttr)

    if currentCat is not None:
        couponsObj = couponsObj.filter(c2p__parent_id__in=category_ids)


    if order != 'ASC':
        orderSymb = '-'

    if sort == 'ed-date':
        couponsObj = couponsObj.order_by(orderSymb + 'item2value__end_date')
    elif sort == 'st-date':
        couponsObj = couponsObj.order_by(orderSymb + 'item2value__start_date')
    elif sort == 'coupon-discount':
        couponsObj = func.sortQuerySetByAttr(couponsObj, "COUPON_DISCOUNT", order, "int")
    else:
        couponsObj = func.sortQuerySetByAttr(couponsObj, "COST", order, "int")

    attr = ("NAME", "COUPON_DISCOUNT", "CURRENCY", "COST", "IMAGE")
    result = func.setPaginationForItemsWithValues(couponsObj, page=page, page_num=16, fullAttrVal=True, *attr)
    page = result[1]
    paginator_range = func.getPaginatorRange(page)
    coupons = func._setCouponsStructure(result[0])

    if order == 'ASC':
        order = 'DESC'
    else:
        order = 'ASC'

    return render_to_response("Coupons/index.html", {'coupons': coupons, 'paginator_range': paginator_range,
                                                     'categories': categories, 'currentCat': currentCatName,
                                                     'breadCrumbs': breadCrumbs, 'nameSpace': 'coupons:category',
                                                     'order': order, 'sort': sort, 'expire': expire},
                                                     context_instance=RequestContext(request))

def couponsDetail(request):
    pass