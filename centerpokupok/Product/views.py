from django.shortcuts import render
from django.shortcuts import render_to_response, get_object_or_404
from appl.models import News, Product, Comment, Category, Company, Country, Cabinet, Order
from core.models import Value, Item, Attribute, Dictionary, Relationship, Slot
from appl import func
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from tppcenter.forms import ItemForm
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.db.models import Q
from collections import OrderedDict
from django.utils.translation import ugettext as _
from django.conf import settings
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.contrib.auth.decorators import login_required
from centerpokupok.forms import OrderForm
from django.db import transaction

def productDetail(request, item_id, page=1):
    if request.POST.get('subCom', False):
        form = addComment(request, item_id)
        if isinstance(form, HttpResponseRedirect):
            return form

    else:
        form = ItemForm("Comment")



    product = get_object_or_404(Product, pk=item_id)
    productValues = product.getAttributeValues("NAME", 'DETAIL_TEXT', 'IMAGE', 'COST', 'CURRENCY', 'DISCOUNT')
    productCoupon = product.getAttributeValues('COUPON_DISCOUNT', fullAttrVal=True)

    category = Category.objects.filter(p2c__child_id=item_id).values_list("pk")
    sameProducts = Product.objects.filter(c2p__parent_id__in=category).exclude(pk=item_id)
    product_id = [prod.id for prod in sameProducts]
    sameProducts = Item.getItemsAttributesValues(("NAME", "IMAGE", "CURRENCY", "COST"), product_id)

    try:
        company = Company.objects.get(p2c__child_id=item_id)
        storeCategories = company.getStoreCategories()
        companyID = company.pk
        company = company.getAttributeValues("NAME")
    except ObjectDoesNotExist:
        pass

    flagList = func.getItemsList("Country", "NAME", "FLAG")

    result = _getComment(item_id, page)
    commentsList = result[0]
    paginator_range = result[1]
    page = result[2]

    dictionaryLabels = {"DETAIL_TEXT": "Comment"}
    form.setlabels(dictionaryLabels)

    url_paginator = "products:paginator"
    url_parameter = [item_id]

    productsPopular = Product.objects.filter(sites=settings.SITE_ID).order_by("-pk")[:5]
    product_id = [prod.id for prod in productsPopular]
    productsPopularList = Item.getItemsAttributesValues(("NAME", "COST", "CURRENCY", "IMAGE"), product_id)

    hierarchyStructure = Category.hierarchy.getTree()
    categories_id = [cat['ID'] for cat in hierarchyStructure]
    categories = Item.getItemsAttributesValues(("NAME",), categories_id)
    categotySelect = func.setStructureForHiearhy(hierarchyStructure, categories)

    root_cats = [cat['ID'] for cat in hierarchyStructure if cat['LEVEL'] == 1]
    storeCategories = func._categoryStructure(hierarchyStructure, storeCategories, categories, root_cats)

    contrySorted = func.sortByAttr("Country", "NAME")
    sorted_id  = [coun.id for coun in contrySorted]
    countryList = Item.getItemsAttributesValues(("NAME",), sorted_id)

    return render_to_response("Product/detail.html", locals(), context_instance=RequestContext(request))

@login_required(login_url="/registration/")
def addComment(request, item_id):

        form = ItemForm("Comment", values=request.POST)
        form.clean()
        spam = Comment.spamCheck(user=request.user, parent_id=item_id)
        if(spam):
            form._errors["DETAIL_TEXT"] = _("You can send one comment per minute")

        if form.is_valid():
            i = request.user
            comment = form.save(request.user)
            parent = Product.objects.get(pk=item_id)
            Relationship.setRelRelationship(parent, comment, request.user)
            return HttpResponseRedirect(reverse("products:detail", args=[item_id]))

        else:
            return form



def getCategoryProduct(request, category_id=None, page=1):

    hierarchyStructure = Category.hierarchy.getTree()

    if category_id is None: #Not filtered by category

        #Get related categories
        #categories = Category.hierarchy.getTree(15)
        categories = hierarchyStructure
        category_root_ids = [cat['ID'] for cat in categories if cat['LEVEL'] == 1]

        #Main Page
        breadCrumbs = None

        #Paginator
        url_parameter = []
        url_paginator = "products:products_paginator"
    else:
        #Get related categories
        category_id = int(category_id)
        categories = Category.hierarchy.getDescendants(category_id)
        category_root_ids = [cat['ID'] for cat in categories if cat['LEVEL'] == 2][:15]

        #creating bread crumbs
        ancestors = Category.hierarchy.getAncestors(category_id)
        ancestors_ids = [cat['ID'] for cat in ancestors]
        breadCrumbs = Product.getItemsAttributesValues(("NAME",), ancestors_ids)

        #Paginator
        url_parameter = [category_id]
        url_paginator = "products:cat_pagination"

    #Products filtered by site
    products = Product.objects.filter(sites=settings.SITE_ID)

    #Main search by categories
    categories_id = [cat['ID'] for cat in hierarchyStructure]
    categoriesAttr = Item.getItemsAttributesValues(("NAME",), categories_id)
    categotySelect = func.setStructureForHiearhy(hierarchyStructure, categoriesAttr)

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

    prodInCat = func.getCountofSepecificItemsRelated('Product', category_ids, products)

    if category_id is not None:
        currentCatName = categoriesAttr[category_id]['NAME'][0]
        category_ids.append(category_id)
        del categoriesAttr[category_id]
    else:
        currentCatName = None

    categories = func._categoryStructure(categories, prodInCat, categoriesAttr, category_root_ids)

    if category_id is not None:
        products = products.filter(c2p__parent_id__in=category_ids, c2p__type='rel', sites=settings.SITE_ID)\
            .order_by("-pk")

    result = func.setPaginationForItemsWithValues(products, "NAME", 'DETAIL_TEXT', 'IMAGE', 'COST', 'CURRENCY',
                                                  'DISCOUNT', 'COUPON_DISCOUNT', page_num=12, page=page)
    products_list = result[0]
    products_ids = [key for key, value in products_list.items()]
    companies = Company.objects.filter(p2c__child_id__in=products_ids)
    items = Item.objects.filter(p2c__child_id__in=companies, p2c__type="rel", pk__in=Country.objects.all(),
                                 p2c__child__p2c__child__in=products_ids).values("country", "p2c__child_id",
                                                                                 'p2c__child__p2c__child', 'pk')
    items_id =[]
    for item in items:
        items_id.append(item['pk'])
        items_id.append(item['p2c__child_id'])

    items_id = set(items_id)
    itemsWithAttribute = Item.getItemsAttributesValues(("NAME", "IMAGE"), items_id)
    companyList = {}
    for item in items:
        products_list[item['p2c__child__p2c__child']].update({'COMPANY_NAME': itemsWithAttribute[item['p2c__child_id']]['NAME']})
        products_list[item['p2c__child__p2c__child']].update({'COMPANY_IMAGE': itemsWithAttribute[item['p2c__child_id']]['IMAGE']})
        products_list[item['p2c__child__p2c__child']].update({'COMPANY_ID': item['p2c__child_id']})
        products_list[item['p2c__child__p2c__child']].update({'COUNTRY_NAME': itemsWithAttribute[item['pk']]['NAME']})
        products_list[item['p2c__child__p2c__child']].update({'COUNTRY_ID': item['pk']})
        if item["p2c__child_id"] not in companyList:
            companyList[item["p2c__child_id"]] = {}
            companyList[item["p2c__child_id"]].update({"COMPANY_NAME": itemsWithAttribute[item['p2c__child_id']]['NAME']})
            companyList[item["p2c__child_id"]].update({"COMPANY_IMAGE": itemsWithAttribute[item['p2c__child_id']]['IMAGE']})
            companyList[item["p2c__child_id"]].update({"COUNTRY_NAME": itemsWithAttribute[item['pk']]['NAME']})
            companyList[item['p2c__child_id']].update({'COUNTRY_ID': item['pk']})



    page = result[1]
    paginator_range = func.getPaginatorRange(page)

    contrySorted = func.sortByAttr("Country", "NAME")
    sorted_id = [coun.id for coun in contrySorted]
    countryList = Item.getItemsAttributesValues(("NAME",), sorted_id)




    return render_to_response("Product/index.html", {'products_list': products_list,'companyList': companyList,
                                                      'page': page, 'paginator_range': paginator_range,
                                                      'url_paginator': url_paginator, 'url_parameter':url_parameter,
                                                      'categotySelect':categotySelect, 'countryList':countryList,
                                                      'categories': categories, 'currentCat': currentCatName,
                                                     'breadCrumbs': breadCrumbs, 'nameSpace': 'products:category'})








def getAllNewProducts(request, page=1):


    products = Product.objects.filter(sites=settings.SITE_ID).order_by("-pk")
    result = func.setPaginationForItemsWithValues(products, "NAME", 'DETAIL_TEXT', 'IMAGE', 'COST', 'CURRENCY',
                                         page_num=15, page=page)
    products_list = result[0]
    products_ids = [key for key, value in products_list.items()]
    companies = Company.objects.filter(p2c__child_id__in=products_ids)
    items = Item.objects.filter(p2c__child_id__in=companies, p2c__type="rel", pk__in=Country.objects.all(),
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
    paginator_range = func.getPaginatorRange(page)
    url_paginator = "products:products_paginator"


    hierarchyStructure = Category.hierarchy.getTree()
    categories_id = [cat['ID'] for cat in hierarchyStructure]
    categories = Item.getItemsAttributesValues(("NAME",), categories_id)
    categotySelect = func.setStructureForHiearhy(hierarchyStructure, categories)


    contrySorted = func.sortByAttr("Country", "NAME")
    sorted_id = [coun.id for coun in contrySorted]
    countryList = Item.getItemsAttributesValues(("NAME",), sorted_id)




    return render_to_response("Product/new.html", {'products_list': products_list, 'page': page,
                                                   'paginator_range':paginator_range, 'url_paginator': url_paginator,
                                                   'categotySelect': categotySelect, 'countryList': countryList})




def _getComment(parent_id, page):
    comments = Comment.getCommentOfItem(parent_id=parent_id)
    comments = comments.order_by('-pk')
    result = func.setPaginationForItemsWithValues(comments, "DETAIL_TEXT", page_num=3, page=page)
    commentsList = result[0]

    for id ,comment in commentsList.items():
        comment['User'] = comments.get(pk=id).create_user
        comment['Date'] = comments.get(pk=id).create_date
    page = result[1]


    paginator_range = func.getPaginatorRange(page)
    commentsList = OrderedDict(sorted(commentsList.items(), reverse=True))

    return commentsList, paginator_range , page

@transaction.atomic
@login_required(login_url="/products/")
def orderProduct(request, step=1):
    curr_url = 'order'
    if step == '1':
        orderForm = ""
        user = request.user
        if not request.session.get('product_id', False) or request.POST.get('product', False):
            request.session['product_id'] = request.POST.get('product', "")
            request.session['qty'] = request.POST.get('french-hens', "")
            if request.session.get("order", False):
                del request.session['order']


        cabinet = Cabinet.objects.get(user=user)
        if request.POST.get('product', False) or not request.session.get("order", False):
             address = cabinet.getAttributeValues("CITY", "COUNTRY", "ZIP", "ADDRESS", "TELEPHONE_NUMBER", "SHIPPING_NAME")
        else:
            session = request.session.get("order", False)
            if session:
                address = {"CITY": [session.get("city", "")], "COUNTRY": [session.get("country", "")],
                           "ZIP": [session.get("zipcode", "")], "ADDRESS": [session.get("address", "")],
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
        productValues = product.getAttributeValues("NAME", "IMAGE", "CURRENCY", "COST")
        totalCost = int(request.session.get('qty', 1)) * int(productValues['COST'][0])
        return render_to_response("Product/orderStepOne.html", {'address': address, 'user': user, "orderForm": orderForm,
                                                                'productValues': productValues ,'totalCost': totalCost,
                                                                'curr_url': curr_url},
                                                                 context_instance=RequestContext(request))

    elif step == '2':
        product_id = request.session.get('product_id', False)
        qty = request.session.get('qty', False)
        product = get_object_or_404(Product, pk=product_id)
        productValues = product.getAttributeValues('NAME', "COST", 'CURRENCY')
        orderDetails = {}
        session = request.session.get("order", " ")
        orderDetails['city'] = session['city']
        orderDetails['country'] = session['country']
        orderDetails['address'] = session['address']
        totalSum = int(productValues['COST'][0]) * int(qty)
        user = request.user

        return render_to_response("Product/orderStepTwo.html", {'qty': qty, 'productValues': productValues,
                                                                'orderDetails': orderDetails, 'totalSum': totalSum,
                                                                "user": user,'curr_url': curr_url})
    else:
        if request.session.get("order", False):
            product = get_object_or_404(Product, pk=request.session.get('product_id'))
            productValues = product.getAttributeValues('NAME', "COST", 'CURRENCY', 'IMAGE')
            qty = request.session.get('qty', False)
            dict = Dictionary.objects.get(title='CURRENCY')
            slot_id = dict.getSlotID(productValues['CURRENCY'][0])
            productValues['CURRENCY'][0] = slot_id
            session = request.session['order']
            address = {"CITY": [session.get("city", "")], "COUNTRY": [session.get("country", "")],
                       "ZIP": [session.get("zipcode", "")], "ADDRESS": [session.get("address", "")],
                       "TELEPHONE_NUMBER": [session.get("telephone_number", "")],
                       "DETAIL_TEXT": [session.get("comment", "")], "SHIPPING_NAME": [session.get("recipient_name", "")]}
            productValues['COST'][0] = int(productValues['COST'][0]) * int(qty)
            with transaction.atomic():
                order = Order(create_user=request.user)
                order.save()
                orderDict = {}
                orderDict.update(productValues)
                orderDict.update(address)
                orderDict.update({"QUANTITY": qty})
                order.setAttributeValue(orderDict, request.user)
                cabinet = Cabinet.objects.get(user=request.user)
                Relationship.setRelRelationship(cabinet, order, request.user)
            del request.session['product_id']
            del request.session['qty']
            del request.session['order']
        else:
            return HttpResponseRedirect("/")

        return render_to_response("Product/orderStepThree.html", {"user": request.user, 'curr_url': curr_url})














