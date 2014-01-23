__author__ = 'user'
from django.shortcuts import render_to_response
from appl import func
from appl.models import Product, Category

def _categoryStructure(categories,  listCount, catWithAttr):

    elCount = {}
    parent = 0

    for dictCount in listCount:
        elCount[dictCount['c2p__parent']] = dictCount['childCount']

    for cat in categories:
        if cat['LEVEL'] == categories[0]['LEVEL']:
            parent = cat['ID']

        if 'count' not in catWithAttr[parent]:
            catWithAttr[parent]['count'] = elCount.get(cat['ID'], 0)
        else:
            catWithAttr[parent]['count'] += elCount.get(cat['ID'], 0)

    return catWithAttr


def couponsList(request, currentCat = None):
    page = request.GET.get('page', 1)

    if currentCat == None:#not filtered list
        categories = Category.hierarchy.getTree(15)
        category_root_ids = [cat['ID'] for cat in categories if cat['LEVEL'] == 1]
        breadCrumbs = None
    else:
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
    prodInCat = func.getCountofSepecificItemsRelated('Product', category_ids, couponsObj)
    categoriesWithAttr = Product.getItemsAttributesValues(("NAME",), category_root_ids)

    if currentCat is not None:
        currentCatName = categoriesWithAttr[currentCat]['NAME'][0]
        category_ids.append(currentCat)
        del categoriesWithAttr[currentCat]
    else:
        currentCatName = None

    categories = _categoryStructure(categories, prodInCat, categoriesWithAttr)

    couponsObj = couponsObj.filter(c2p__parent_id__in=category_ids).order_by('item2value__end_date')

    attr = ("NAME", "COUPON_DISCOUNT", "CURRENCY", "COST", "IMAGE")
    result = func.setPaginationForItemsWithValues(couponsObj, page=page, page_num=16, fullAttrVal=True, *attr)
    page = result[1]
    paginator_range = func.getPaginatorRange(page)
    coupons = func._setCouponsStructure(result[0])



    return render_to_response("Coupons/index.html", {'coupons': coupons, 'paginator_range': paginator_range,
                                                     'categories': categories, 'currentCat': currentCatName,
                                                     'breadCrumbs': breadCrumbs})

def couponsDetail(request):
    pass