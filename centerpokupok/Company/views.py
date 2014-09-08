from django.http import HttpResponseNotFound
from django.utils.timezone import now
from haystack.backends import SQ
from haystack.query import SearchQuerySet
from centerpokupok.Product.views import getProductList
from centerpokupok.cbv import ItemsList

__author__ = 'user'
from core.models import Item
from appl.models import Company, Category, Product, Comment, Favorite
from django.shortcuts import render_to_response, get_object_or_404
from appl import func
from django.conf import settings
from django.db.models import Count
from django.template import RequestContext


def storeMain(request, company, category=None):

    if not Company.objects.filter(pk=company).exists():
        return HttpResponseNotFound()


    #----NEW PRODUCT LIST -----#
    newProducrList = SearchQuerySet().models(Product).filter(sites=settings.SITE_ID, company=company)\
        .order_by('-obj_create_date')[:4]

    if category:
        newProducrList = newProducrList.filter(categories=category)

    #----NEW PRODUCT LIST -----#
    products = Product.getTopSales().filter(sites=settings.SITE_ID)

    products = products.filter(c2p__parent_id=company)

    if category:
        products = products.filter(c2p__parent_id=category)

    products = [prd.pk for prd in products[:4]]

    topPoductList = SearchQuerySet().models(Product).filter(django_id__in=products)

    #------ 3 Coupons ----------#
    coupons = SearchQuerySet().models(Product).filter(sites=settings.SITE_ID, coupon__gt=0,
                                                         coupon_end__gt=now(), coupon_start__lte=now(),
                                                         company=company).order_by('coupon_end')[:3]

    #----------- Products with discount -------------#
    productsSale = SearchQuerySet().models(Product)\
        .filter(SQ(coupon=0) | SQ(coupon_end__lte=now()) | SQ(coupon_start__gt=now()),
                sites=settings.SITE_ID, company=company, discount__gt=0).order_by('-discount')[:15]

    templateParams = {
        'companyID': company,
        'coupons': coupons,
        'productsSale': productsSale,
        'newProducrList': newProducrList,
        'topPoductList': topPoductList, 'menu': 'main',
        'store_url': 'companies:category'
    }


    return render_to_response("Company/index.html", templateParams, context_instance=RequestContext(request))

def about(request, company):
    if not Company.objects.filter(pk=company).exists():
        return HttpResponseNotFound()


    templateParams = {
        'companyID': company,
        'detail_text': SearchQuerySet().models(Company).filter(django_id=company)[0].text,
    }

    return render_to_response("Company/about.html", templateParams, context_instance=RequestContext(request))

def contact(request, company):

    if not Company.objects.filter(pk=company).exists():
        return HttpResponseNotFound()


    templateParams = {
        'companyID': company,
    }

    return render_to_response("Company/contact.html", templateParams, context_instance=RequestContext(request))

class companyProductList(ItemsList):

    model = Product
    template_name = "Company/products.html"

    def get_context_data(self, **kwargs):
        context = super(companyProductList, self).get_context_data(**kwargs)

        context['favorite'] = self._get_favorites(context['object_list'])
        context['companyID'] = self.kwargs.get('company')

        return context

    def get_queryset(self):
        sqs = super(companyProductList, self).get_queryset()

        company = self.kwargs.get('company')

        sqs = sqs.filter(company=company)

        q = self.request.GET.get('q', '')

        if q:
            return sqs.filter(title=q)

        return sqs

'''
def products(request, company, category=None, page=1):

    companyObj = get_object_or_404(Company, pk=company)

    filter = {}

    if category:
        categories = Category.hierarchy.getDescendants(category)
        category_ids = [cat['ID'] for cat in categories]
        filter['c2p__parent_id__in'] = category_ids

    products = Product.getNew().filter(sites=settings.SITE_ID, c2p__parent_id=company).filter(**filter)


    #Product list , with companies and countries
    products = result[0]
    products_ids = [key for key, value in products.items()]
    favorites_dict = {}
    if request.user.is_authenticated():
        favorites = Favorite.objects.filter(c2p__parent__cabinet__user=request.user, p2c__child__in=products_ids).values("p2c__child")
        for favorite in favorites:
            favorites_dict[favorite['p2c__child']] = 1


    comments = Comment.objects.filter(c2p__parent__in=products_ids).values("c2p__parent").annotate(num_comments=Count("c2p__parent"))
    comment_dict = {}
    for comment in comments:
        comment_dict[comment['c2p__parent']] = comment['num_comments']

    for id, product in products.items():
        toUpdate = {'COMMENTS': comment_dict.get(id, 0),
                    'FAVORITE': favorites_dict.get(id, 0)}
        product.update(toUpdate)
    #Paginator
    page = result[1]
    paginator_range = func.getPaginatorRange(page)

    if category:
        url_paginator = "companies:products_category_paged"
        url_parameter = [company, category]
    else:
        url_paginator = "companies:products_paged"
        url_parameter = [company]

    return render_to_response("Company/products.html", {'companyID': company, 'name': name, 'picture': picture,
                                                        'storeCategories': storeCategories, 'products': products,
                                                        'menu': 'products','store_url': 'companies:products_category',
                                                        'page': page, 'paginator_range': paginator_range,
                                                        'url_paginator': url_paginator, 'url_parameter':url_parameter,
                                                        'popular': popular, 'user': request.user},
                              context_instance=RequestContext(request))


def coupons(request, company, category=None, page=1):
    companyObj = get_object_or_404(Company, pk=company)

    filter = {}

    if category:
        categories = Category.hierarchy.getDescendants(category)
        category_ids = [cat['ID'] for cat in categories]
        filter['c2p__parent_id__in'] = category_ids

    coupons = Product.getCoupons()

    popular = Product.getTopSales().filter(sites=settings.SITE_ID)[:4]
    popular = [prd.pk for prd in popular]

    popular = Product.getItemsAttributesValues(("NAME", "COST", "CURRENCY", "IMAGE", 'COUPON_DISCOUNT','DISCOUNT'),
                                                     popular)

    #------------------- Company Details --------------------#
    attr = companyObj.getAttributeValues('NAME', 'IMAGE')
    name = attr['NAME'][0]
    picture = attr.get('IMAGE', [''])[0]

    #-------------- Store Categories ---------------#
    storeCategories = companyObj.getStoreCategories(coupons)
    hierarchyStructure = Category.hierarchy.getTree(siteID=settings.SITE_ID)
    root_cats = [cat['ID'] for cat in hierarchyStructure if cat['LEVEL'] == 1]
    categories = Item.getItemsAttributesValues(("NAME",), root_cats)

    storeCategories = func._categoryStructure(hierarchyStructure, storeCategories, categories)

    coupons = coupons.filter(sites=settings.SITE_ID, c2p__parent_id=company).filter(**filter)

    result = func.setPaginationForItemsWithValues(coupons, "NAME", 'DETAIL_TEXT', 'IMAGE', 'COST', 'CURRENCY',
                                                 'DISCOUNT', 'COUPON_DISCOUNT', page_num=16, page=page, fullAttrVal=True)
    #Product list , with companies and countries
    coupons = result[0]
    coupons = func._setCouponsStructure(coupons)

    #Paginator
    page = result[1]
    paginator_range = func.getPaginatorRange(page)

    if category:
        url_paginator = "companies:coupons_category_paged"
        url_parameter = [company, category]
    else:
        url_paginator = "companies:coupons_paged"
        url_parameter = [company]

    return render_to_response("Company/coupons.html", {'companyID': company, 'name': name, 'picture': picture,
                                                       'storeCategories': storeCategories, 'menu': 'coupons',
                                                       'store_url': 'companies:coupons_category', 'page': page,
                                                       'paginator_range': paginator_range, 'url_paginator':url_paginator,
                                                       'url_parameter': url_parameter, 'coupons': coupons,
                                                       'popular': popular, 'user': request.user},
                              context_instance=RequestContext(request))
'''


class companyCoupontList(ItemsList):

    model = Product
    template_name = "Company/coupons.html"

    def get_context_data(self, **kwargs):
        context = super(companyCoupontList, self).get_context_data(**kwargs)

        context['companyID'] = self.kwargs.get('company')

        return context

    def get_queryset(self):
        sqs = super(companyCoupontList, self).get_queryset()

        company = self.kwargs.get('company')

        return sqs.filter(coupon__gt=0, coupon_end__gt=now(), coupon_start__lte=now(), company=company)
