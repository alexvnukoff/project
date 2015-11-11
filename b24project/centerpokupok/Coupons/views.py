
from centerpokupok.cbv import ItemsList
from core.models import Item

__author__ = 'user'

from django.shortcuts import render_to_response
from appl import func
from appl.models import Product, Category, Company
from django.template import RequestContext
from django.utils.timezone import now
from datetime import timedelta
from django.conf import settings

'''
def couponsList(request, currentCat = None, page=1, country=None):
    sort = request.GET.get('sort', 'ed-date')
    order = request.GET.get('order', 'ASC')
    expire = request.GET.get('expire', None)
    orderSymb = ''

    if currentCat == None:#not filtered list

        #Getting related categories
        categories = Category.hierarchy.getTree(15, siteID=settings.SITE_ID)
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

    if country:
        companies = Company.active.get_active_related().filter(c2p__parent_id=country)
        couponsObj = couponsObj.filter(c2p__parent__in=companies)

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

    #----------- Sorting --------#
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


    #Setting urls name
    url_country = 'coupons:list_country'
    url_country_parametr = []

    url_paginator = "coupons:list_paged"
    url_parameter = []

    category_url = 'coupons:category'
    category_parameters = []

    if country and currentCat:
        url_paginator = "coupons:category_country_paged"
        url_parameter = [country, currentCat]

        url_country = 'coupons:category_country'
        url_country_parametr = [currentCat]

        category_url = 'coupons:category_country'
        category_parameters = [country]
    elif country:
        url_paginator = "coupons:list_country_paged"
        url_parameter = [country]

        category_url = 'coupons:category_country'
        category_parameters = [country]

    elif currentCat:
        url_paginator = "coupons:category_paged"
        url_parameter = [currentCat]

        url_country = 'coupons:category_country'
        url_country_parametr = [currentCat]



    return render_to_response("Coupons/index.html", {'coupons': coupons, 'paginator_range': paginator_range,
                                                     'categories': categories, 'currentCat': currentCatName,
                                                     'breadCrumbs': breadCrumbs, 'nameSpace': 'coupons:category',
                                                     'order': order, 'sort': sort, 'expire': expire, 'country': country,
                                                     'url_paginator': url_paginator, 'url_parameter': url_parameter,
                                                     'url_country': url_country,
                                                     'url_country_parametr':url_country_parametr,
                                                     'category_url': category_url,
                                                     'category_parameters': category_parameters},
                                                     context_instance=RequestContext(request))

'''


class companyCoupontList(ItemsList):

    model = Product
    template_name = "Coupons/index.html"

    def _get_breadcrumb(self):

        if self.category:
            ancestors = Category.hierarchy.getAncestors(self.category)
            ancestors_ids = [cat['ID'] for cat in ancestors]
            return SearchQuerySet().models(Category).filter(django_id__in=ancestors_ids)

        return None

    def _get_current_category(self):

        if self.category:
            return SearchQuerySet().models(Category).filter(django_id=self.category)[0]

        return None

    def _get_categories(self, limit=5):

        sqs = SearchQuerySet().models(Category).filter(sites=settings.SITE_ID)

        if self.category:

            child = sqs.filter(parent=self.category)

            if child.count() > 0:
                return child

            sib = Item.objects.get(pk=self.category).getSiblings(includeSelf=False)

            if sib:
                return sqs.filter(django_id__in=[cat.pk for cat in sib])[:limit]

            return sqs.filter(parent=0).exclude(django_id=self.category)[:limit]

        return sqs.filter(parent=0)[:limit]


    def get_context_data(self, **kwargs):
        context = super(companyCoupontList, self).get_context_data(**kwargs)

        context['breadcrumb'] = self._get_breadcrumb()
        context['currentCat'] = self._get_current_category()
        context['categories'] = self._get_categories()
        context['category_namespace'] = "coupons:category"

        return context

    def get_queryset(self):
        sqs = super(companyCoupontList, self).get_queryset()

        return sqs.filter(coupon__gt=0, coupon_end__gt=now(), coupon_start__lte=now())
