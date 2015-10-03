from collections import OrderedDict
import json

from django.shortcuts import render_to_response, get_object_or_404
from haystack.query import SearchQuerySet
from django.http import Http404, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.conf import settings
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db import transaction

from appl.models import Product, Comment, Category, Company, Country, Cabinet, Order, Favorite
from centerpokupok.cbv import ItemsList
from core.models import Item, Dictionary, Relationship
from appl import func
from b24online.forms import ItemForm
from centerpokupok.forms import OrderForm


def productDetail(request, item_id, page=1):

    if request.POST.get('subCom', False):
        form = addComment(request, item_id)
        if isinstance(form, HttpResponseRedirect):
            return form
    else:
        form = ItemForm("Comment")

    product = get_object_or_404(Product, pk=item_id)

    productValues = SearchQuerySet().models(Product).filter(django_id=item_id)[0]

    sameProducts = SearchQuerySet().models(Product).filter(categories__in=productValues.categories).exclude(django_id=item_id)[:4]
    #-------- Comments ----------------#
    result = _getComment(item_id, page)
    commentsList = result[0]
    paginator_range = result[1]
    page = result[2]

    dictionaryLabels = {"DETAIL_TEXT": _("Comment")}
    form.setlabels(dictionaryLabels)

    store_url = 'companies:products_category'

    favorite = 0

    if request.user.is_authenticated():
        try:
            favorite = Favorite.active.get_active_related().get(c2p__parent__cabinet__user=request.user, p2c__child=item_id)
        except ObjectDoesNotExist:
            pass

    templateParams = {
        'productValues': productValues,
        'sameProducts': sameProducts,
        'commentsList': commentsList,
        'paginator_range': paginator_range,
        'page': page,
        'store_url': store_url,
        'favorite': favorite,
        'company': SearchQuerySet().models(Company).filter(django_id=productValues.company)[0]
    }

    return render_to_response("Product/detail.html", templateParams, context_instance=RequestContext(request))


def addComment(request, item_id):
        if not request.user.is_authenticated():
           url_product = reverse("products:detail", args=[item_id])
           return HttpResponseRedirect("/registration/?next=%s" %url_product)

        form = ItemForm("Comment", values=request.POST)
        form.clean()
        spam = Comment.spamCheck(user=request.user, parent_id=item_id)
        if(spam):
            form._errors["DETAIL_TEXT"] = _("You can send one comment per minute")

        if form.is_valid():
            i = request.user
            comment = form.save(request.user, settings.SITE_ID, disableNotify=True)
            parent = Product.objects.get(pk=item_id)
            Relationship.setRelRelationship(parent, comment, request.user)
            return HttpResponseRedirect(reverse("products:detail", args=[item_id]))

        else:
            return form


class getProductList(ItemsList):

    model = Product
    template_name = "Product/index.html"

    def _get_sellers(self, object_list):
        sellers_ids = [obj.company for obj in object_list]

        return SearchQuerySet().models(Company).filter(django_id__in=sellers_ids)

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
        context = super(getProductList, self).get_context_data(**kwargs)


        context['breadcrumb'] = self._get_breadcrumb()
        context['favorite'] = self._get_favorites(context['object_list'])
        context['currentCat'] = self._get_current_category()
        context['sellers'] = self._get_sellers(context['object_list'])
        context['categories'] = self._get_categories()
        context['category_namespace'] = "products:category"

        return context

    def get_queryset(self):


        sqs = super(getProductList, self).get_queryset()

        q = self.request.GET.get('q', '')

        if q:
            return sqs.filter(title=q)

        return sqs


'''
def getCategoryProduct(request, country=None, category_id=None, page=1):
    url_country = "products:country_products"
    url_country_parametr = []


    if category_id is None: #Not filtered by category

        #Get related categories
        category_root_ids = SearchQuerySet().models(Category).filter(parent=0)

        #Main Page
        breadCrumbs = None

        #Paginator
        if country:
            url_parameter = [country]
            url_paginator = "products:country_products_paginator"
            category_url = "products:category_country"
            category_parameters = [country]
        else:
            url_parameter = []
            url_paginator = "products:products_paginator"
            category_url = "products:category"
            category_parameters = []

    else:
        #Get related categories
        category_id = int(category_id)
        categories = Category.hierarchy.getDescendants(category_id)
        category_root_ids = [cat['ID'] for cat in categories if cat['LEVEL'] == 2][:15]

        #creating bread crumbs
        ancestors = Category.hierarchy.getAncestors(category_id)
        ancestors_ids = [cat['ID'] for cat in ancestors]
        breadCrumbs = SearchQuerySet().models(Category).filter(django_id__in=ancestors_ids)

        #Paginator
        url_country = "products:category_country"
        url_country_parametr = [category_id]

        if country:
            category_url = "products:category_country"
            category_parameters = [country]
            url_parameter = [country, category_id]
            url_paginator = "products:category_country_paginator"
        else:
            category_url = "products:category"
            category_parameters = []
            url_parameter = [category_id]
            url_paginator = "products:cat_pagination"

    products = func.getActiveSQS().models(Product).filter(sites=settings.SITE_ID)

    if country:
        products = products.filter(country=country)

    #Related categories list with descendants
    category_ids = [cat['ID'] for cat in categories]

    #sort categories
    rootCats = Category.objects.filter(pk__in=category_root_ids)
    sortedRootCat = func.sortQuerySetByAttr(rootCats, "NAME", "ASC", "str")

    #Related categories list without descendants
    category_root_ids = [cat.pk for cat in sortedRootCat]

    #Get categories attributes & count
    if category_id is not None:
        category_root_ids.insert(0, category_id)
        category_ids.append(category_id)
    else:
        currentCatName = None

    SearchQuerySet().models(Category).filter(django_id__in=category_root_ids)

    if category_id is not None:
        products = products.filter(categories=category_id)

    #Product list , with companies and countries
    products_ids = [key for key, value in products_list.items()]
    favorites_dict = {}

    if request.user.is_authenticated():
        favorites = Favorite.active.get_active_related().filter(c2p__parent__cabinet__user=request.user, p2c__child__in=products_ids).values("p2c__child")
        for favorite in favorites:
            favorites_dict[favorite['p2c__child']] = 1


    comments = Comment.objects.filter(c2p__parent__in=products_ids).values("c2p__parent").annotate(num_comments=Count("c2p__parent"))
    comment_dict = {}
    for comment in comments:
        comment_dict[comment['c2p__parent']] = comment['num_comments']

    companies = Company.active.get_active_related().filter(p2c__child_id__in=products_ids)
    items = Item.objects.filter(p2c__child_id__in=companies, p2c__type="dependence", pk__in=Country.active.get_active().all(),
                                 p2c__child__p2c__child__in=products_ids).values("country", "p2c__child_id",
                                                                                 'p2c__child__p2c__child', 'pk')
    items_id = []
    for item in items:
        items_id.append(item['pk'])
        items_id.append(item['p2c__child_id'])


    items_id = set(items_id)
    itemsWithAttribute = Item.getItemsAttributesValues(("NAME", "IMAGE"), items_id)
    companyList = {}

    for item in items:
        toUpdate = {'COMPANY_NAME': itemsWithAttribute[item['p2c__child_id']].get('NAME', [0]),
                    'COMPANY_IMAGE': itemsWithAttribute[item['p2c__child_id']].get('IMAGE', [0]),
                    'COMPANY_ID': item['p2c__child_id'],
                    'COUNTRY_NAME': itemsWithAttribute[item['pk']].get('NAME', [0]),
                    'COUNTRY_ID': item['pk'],
                    'COMMENTS': comment_dict.get(item['p2c__child__p2c__child'], 0),
                    'FAVORITE': favorites_dict.get(item['p2c__child__p2c__child'], 0)}
        products_list[item['p2c__child__p2c__child']].update(toUpdate)






        if item["p2c__child_id"] not in companyList:
            companyList[item["p2c__child_id"]] = {}
            companyList[item["p2c__child_id"]].update(
                {"COMPANY_NAME": itemsWithAttribute[item['p2c__child_id']]['NAME']})
            companyList[item["p2c__child_id"]].update({"COMPANY_IMAGE": itemsWithAttribute[item['p2c__child_id']].get('IMAGE',[''])})
            companyList[item["p2c__child_id"]].update({"COUNTRY_NAME": itemsWithAttribute[item['pk']]['NAME']})
            companyList[item['p2c__child_id']].update({'COUNTRY_ID': item['pk']})


    #Paginator
    paginator_range = func.getPaginatorRange(page)

    return render_to_response("Product/index.html", {'companyList': companyList,
                                                     'page': page, 'paginator_range': paginator_range,
                                                     'url_paginator': url_paginator, 'url_parameter' :url_parameter,
                                                     'categories': categories, 'country': country,
                                                     'currentCat': currentCatName, 'breadCrumbs': breadCrumbs,
                                                     'category_url': category_url, 'url_country': url_country,
                                                     'url_country_parametr': url_country_parametr,
                                                     'category_parameters': category_parameters,
                                                     'user': request.user}, context_instance=RequestContext(request))
'''

def getAllNewProducts(request, page=1):


    products = Product.objects.filter(sites=settings.SITE_ID).order_by("-pk")
    result = func.setPaginationForItemsWithValues(products, "NAME", 'DETAIL_TEXT', 'IMAGE', 'COST', 'CURRENCY',
                                         page_num=15, page=page)
    products_list = result[0]
    products_ids = [key for key, value in products_list.items()]
    companies = Company.objects.filter(p2c__child_id__in=products_ids)
    items = Item.objects.filter(p2c__child_id__in=companies, p2c__type="dependence", pk__in=Country.objects.all(),
                                 p2c__child__p2c__child__in=products_ids).values("country", "p2c__child_id",
                                                                                 'p2c__child__p2c__child', 'pk')
    items_id =[]
    for item in items:
        items_id.append(item['pk'])
        items_id.append(item['p2c__child_id'])

    items_id = set(items_id)
    itemsWithAttribute = Item.getItemsAttributesValues(("NAME", "IMAGE"), items_id)

    for item in items:
        products_list[item['p2c__child__p2c__child']].update({'COMPANY_NAME': itemsWithAttribute[item['p2c__child_id']]['NAME']})
        products_list[item['p2c__child__p2c__child']].update({'COMPANY_IMAGE': itemsWithAttribute[item['p2c__child_id']]['IMAGE']})
        products_list[item['p2c__child__p2c__child']].update({'COMPANY_ID': item['p2c__child_id']})
        products_list[item['p2c__child__p2c__child']].update({'COUNTRY_NAME': itemsWithAttribute[item['pk']]['NAME']})
        products_list[item['p2c__child__p2c__child']].update({'COUNTRY_ID': item['pk']})




    page = result[1]
    paginator_range = func.get_paginator_range(page)

    url_paginator = "products:products_paginator"












    return render_to_response("Product/new.html", {'products_list': products_list, 'page': page,
                                                   'paginator_range':paginator_range, 'url_paginator': url_paginator,
                                                   'user': request.user}, context_instance=RequestContext(request))




def _getComment(parent_id, page):
    comments = Comment.getCommentOfItem(parent_id=parent_id)
    comments = comments.order_by('-pk')
    result = func.setPaginationForItemsWithValues(comments, "DETAIL_TEXT", page_num=3, page=page)
    commentsList = result[0]

    for id ,comment in commentsList.items():
        comment['User'] = comments.get(pk=id).create_user
        comment['Date'] = comments.get(pk=id).create_date
    page = result[1]


    paginator_range = func.get_paginator_range(page)
    commentsList = OrderedDict(sorted(commentsList.items(), reverse=True))

    return commentsList, paginator_range, page

@transaction.atomic
def orderProduct(request, step=1):
#------ Order of products in threee step ----#
    if not request.user.is_authenticated():
        url_product = reverse("products:detail", args=[request.POST.get('product', 1)])
        return HttpResponseRedirect("/registration/?next=%s" %url_product)


    contrySorted = func.sortByAttr("Country", "NAME")
    sorted_id = [coun.id for coun in contrySorted]
    countryList = Item.getItemsAttributesValues(("NAME",), sorted_id)

    curr_url = 'order'
    if step == '1':
        #-----Step One , form of shipping addres plus deleviry method ---#
        orderForm = ""
        user = request.user
        if not request.session.get('product_id', False) or request.POST.get('product', False):
            request.session['product_id'] = request.POST.get('product', "")
            request.session['qty'] = request.POST.get('french-hens', "")
            if request.session.get("order", False):
                del request.session['order']


        cabinet = Cabinet.objects.get(user=user)
        if request.POST.get('product', False) or not request.session.get("order", False):
             address = cabinet.getAttributeValues("ADDRESS_CITY", "ADDRESS_COUNTRY", "ADDRESS_ZIP", "ADDRESS", "TELEPHONE_NUMBER", "SHIPPING_NAME")
        else:
            session = request.session.get("order", False)
            if session:
                address = {"ADDRESS_CITY": [session.get("city", "")], "ADDRESS_COUNTRY": [session.get("country", "")],
                           "ADDRESS_ZIP": [session.get("zipcode", "")], "ADDRESS": [session.get("address", "")],
                           "TELEPHONE_NUMBER": [session.get("telephone_number", "")],
                           "SHIPPING_NAME": [session.get("recipient_name", "")]}


        if request.POST.get("Continue", False):
            orderForm = OrderForm(request.POST)
            if orderForm.is_valid():
                if request.POST.get("delivery", False):
                    request.session['order'] = request.POST
                    return HttpResponseRedirect(reverse("products:order", args=['2']))

                else:
                    orderForm.errors.update({"delivery": "Required deleviry method"})
        product = get_object_or_404(Product, pk=request.session.get("product_id", " "))
        productValues = product.getAttributeValues("NAME", "IMAGE", "CURRENCY", "COST", 'DISCOUNT', 'COUPON_DISCOUNT')
        productValues['COST'][0] = _getRealCost(productValues)
        totalCost = float( productValues['COST'][0]) * float(request.session.get('qty', 1))



        return render_to_response("Product/orderStepOne.html", {'address': address, 'user': user, "orderForm": orderForm,
                                                                'productValues': productValues ,'totalCost': totalCost,
                                                                'curr_url': curr_url},
                                                                 context_instance=RequestContext(request))

    elif step == '2':
        #----Step two , checkout , and conformation  of order----#
        product_id = request.session.get('product_id', False)
        qty = request.session.get('qty', False)
        product = get_object_or_404(Product, pk=product_id)
        productValues = product.getAttributeValues('NAME', "COST", 'CURRENCY', 'DISCOUNT', 'COUPON_DISCOUNT')
        orderDetails = {}
        session = request.session.get("order", " ")
        orderDetails['city'] = session['city']
        orderDetails['country'] = session['country']
        orderDetails['address'] = session['address']
        productValues['COST'][0] = _getRealCost(productValues)
        totalSum = float(productValues['COST'][0]) * float(request.session.get('qty', 1))


        user = request.user

        return render_to_response("Product/orderStepTwo.html", {'qty': qty, 'productValues': productValues,
                                                                'orderDetails': orderDetails, 'totalSum': totalSum,
                                                                "user": user,'curr_url': curr_url,
                                                                },context_instance=RequestContext(request))
    else:
        #-----Step three , cleaning of sessions , and creatin of new order object that related to cabinet of user ---#
        if request.session.get("order", False):
            product = get_object_or_404(Product, pk=request.session.get('product_id'))
            productValues = product.getAttributeValues('NAME', "COST", 'CURRENCY', 'IMAGE', 'DISCOUNT', 'COUPON_DISCOUNT')
            qty = request.session.get('qty', False)
            dict = Dictionary.objects.get(title='CURRENCY')
            slot_id = dict.getSlotID(productValues['CURRENCY'][0])
            productValues['CURRENCY'][0] = slot_id
            session = request.session['order']
            address = {"ADDRESS_CITY": [session.get("city", "")], "ADDRESS_COUNTRY": [session.get("country", "")],
                       "ADDRESS_ZIP": [session.get("zipcode", "")], "ADDRESS": [session.get("address", "")],
                       "TELEPHONE_NUMBER": [session.get("telephone_number", "")],
                       "DETAIL_TEXT": [session.get("comment", "")], "SHIPPING_NAME": [session.get("recipient_name", "")]}
            productValues['COST'][0] = float(_getRealCost(productValues)) * float(qty)
            with transaction.atomic():
                order = Order(create_user=request.user)
                order.save()
                orderDict = {}
                orderDict.update(productValues)
                orderDict.update(address)
                orderDict.update({"QUANTITY": qty})
                del orderDict['CREATE_DATE']
                order.setAttributeValue(orderDict, request.user)
                cabinet = Cabinet.objects.get(user=request.user)
                Relationship.setRelRelationship(cabinet, order, request.user)
                Relationship.setRelRelationship(order, product, request.user)
            del request.session['product_id']
            del request.session['qty']
            del request.session['order']
        else:
            return HttpResponseRedirect("/")

        return render_to_response("Product/orderStepThree.html", {"user": request.user, 'curr_url': curr_url },
                                  context_instance=RequestContext(request))



def _getRealCost(productValues):
     if productValues.get('COUPON_DISCOUNT', False):
            totalCost = (float(productValues['COST'][0]) -
                   float(productValues['COST'][0])*(float(productValues['COUPON_DISCOUNT'][0])/100))
     elif productValues.get('DISCOUNT', False) and not productValues.get('COUPON_DISCOUNT', False):
            totalCost = (float(productValues['COST'][0]) -
                   float(productValues['COST'][0])*(float(productValues['DISCOUNT'][0])/100))
     else:
             totalCost = int(productValues['COST'][0])

     return  totalCost

@transaction.atomic
@ensure_csrf_cookie
def addFavorite(request):
    if request.is_ajax():
        result = {"RESULT": {"TYPE": "ERROR", "MESS": "ERROR"}}
        product_id = int(request.POST.get('ID'))
        user = request.user
        try:
            favProduct = Favorite.objects.get(p2c__child_id=product_id, c2p__parent__cabinet__user=user)
            favProduct.delete()
            result = {"RESULT": {"TYPE": "OK", "MESS": "DELETE"}}
        except ObjectDoesNotExist:
            with transaction.atomic():
                favProduct = Favorite(create_user=user)
                favProduct.save()
                cabinet = get_object_or_404(Cabinet, user=user)
                product = get_object_or_404(Product, pk=product_id)
                Relationship.setRelRelationship(favProduct, product, user)
                Relationship.setRelRelationship(cabinet, favProduct, user, type='dependence')
                result = {"RESULT": {"TYPE": "OK", "MESS": "ADD"}}



        return HttpResponse(json.dumps(result))
    else:
        raise Http404





















