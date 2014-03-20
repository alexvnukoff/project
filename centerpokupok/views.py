from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from appl.models import News, Category, Country, Tpp, Review, Product, Cabinet, Order, Company
from registration.backends.default.views import RegistrationView
from core.models import Value, Item, Attribute, Dictionary, Relationship, User
from django.db.models import Count
from registration.forms import RegistrationFormUniqueEmail
from appl import func
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _
from django.conf import settings


def home(request, country=None):


    #----NEW PRODUCT LIST -----#
    if country:
        productQuery = Product.active.get_active_related().filter(c2p__parent__c2p__parent=country, c2p__parent__in=Company.objects.all())
        products = Product.getNew(productQuery).filter(sites=settings.SITE_ID).order_by("-pk")[:4]
    if not country:
        products = Product.getNew().filter(sites=settings.SITE_ID).order_by("-pk")[:4]


    newProducrList = Product.getCategoryOfPRoducts(products, ("NAME", "COST", "CURRENCY", "IMAGE", "DISCOUNT",
                                                              "COUPON_DISCOUNT"))

    #----NEW PRODUCT LIST -----#
    if not country:
        products = Product.getNew().filter(sites=settings.SITE_ID).order_by("-pk")[:4]
    else:
        products = Product.getTopSales(productQuery)[:4]

    topPoductList = Product.getCategoryOfPRoducts(products, ("NAME", "COST", "CURRENCY", "IMAGE", "DISCOUNT",
                                                              "COUPON_DISCOUNT"))

     #----MAIN MENU AND CATEGORIES IN HEADER ------#
    hierarchyStructure = Category.hierarchy.getTree(siteID=settings.SITE_ID)
    categories_id = [cat['ID'] for cat in hierarchyStructure]
    categories = Item.getItemsAttributesValues(("NAME",), categories_id)
    categotySelect = func.setStructureForHiearhy(hierarchyStructure, categories)  # Select of categories

    hierarchyStructure = hierarchyStructure


    sortedHierarchyStructure = _sortMenu(hierarchyStructure) if len(hierarchyStructure) > 0 else {}
    level = 0
    for node in sortedHierarchyStructure:
        node['pre_level'] = level
        node['item'] = categories[node['ID']]
        node['parent_item'] = categories[node['PARENT_ID']] if node['PARENT_ID'] is not None else ""
        level = node['LEVEL']


    #get 3 active coupons ordered by end date
    #---------COUPONS----------#
    if not country:
         couponsObj = Product.getCoupons().order_by('item2value__end_date')[:3]
    else:
        couponsObj = Product.getCoupons(querySet=productQuery).order_by('item2value__end_date')[:3]
    coupons_ids = [cat.pk for cat in couponsObj]

    coupons = Product.getItemsAttributesValues(("NAME", "COUPON_DISCOUNT", "CURRENCY", "COST", "IMAGE"), coupons_ids,
                                               fullAttrVal=True)
    coupons = func._setCouponsStructure(coupons)

    #----------- Products with discount -------------#
    if not country:
          productsSale = Product.getProdWithDiscount()
    else:
          productsSale = Product.getProdWithDiscount(productQuery)

    productsSale = func.sortQuerySetByAttr(productsSale, "DISCOUNT", "DESC", "int")[:15]
    productsSale_ids = [prod.pk for prod in productsSale]
    productsSale = Product.getItemsAttributesValues(("NAME", "DISCOUNT", "IMAGE", "COST"), productsSale_ids)




    url_country = "home_country"





    user = request.user

    return render_to_response("index.html", {'sortedHierarchyStructure': sortedHierarchyStructure,
                                             'coupons': coupons, "newProducrList": newProducrList,
                                             "topPoductList": topPoductList, "productsSale": productsSale,
                                             'user': user, 'url_country': url_country,
                                             'country': country}, context_instance=RequestContext(request))


def about(request):

    return render_to_response("About/About.html")

def set_news_list(request):
    page = request.GET.get('page', 1)
    result = func.getItemsListWithPagination("News", "Anons", "DETAIL_TEXT", "IMAGE", page=page)

    itemsList = result[0]
    page = result[1]
    return render_to_response('NewsList.html', locals())


def _sortMenu(hierarchyStructure):
    count = 0
    sortedHierarchyStructure = []
    dictToSort = []
    id = hierarchyStructure[0]['ID']
    for i in range(0, len(hierarchyStructure)):
        if hierarchyStructure[i]["LEVEL"] == 1 and hierarchyStructure[i]['ID'] != id:
            if count == 9:
                break
            id = hierarchyStructure[i]['ID']
            sortedHierarchyStructure.extend(_sortList(dictToSort))
            dictToSort = []
            count += 1

        dictToSort.append(hierarchyStructure[i])

    if len(dictToSort) > 0:
       sortedHierarchyStructure.extend(_sortList(dictToSort))

    return sortedHierarchyStructure

def _sortList(dict):
    sortedDict = []
    i = 0
    while i < len(dict):
        if dict[i]['LEVEL'] > 3:
            dict.pop(i)
            i-= 1
        if dict[i]['ISLEAF'] == 1 and dict[i]["LEVEL"] == 2:
            sortedDict.append(dict.pop(i))
            i -= 1
        i+=1

    dict.extend(sortedDict)
    return dict


def registration(request, form, auth_form):
   if request.user.is_authenticated():
      return HttpResponseRedirect("/")

   if request.POST.get('Register', None):
     form = RegistrationFormUniqueEmail(request.POST)
     if form.is_valid() and request.POST.get('tos', None):
        cleaned = form.cleaned_data
        reg_view = RegistrationView()
        try:
            reg_view.register(request, **cleaned)
            return render_to_response("registration/registration_complete.html", locals())
        except ValueError:
            return render_to_response("registration/registration_closed.html")
     else:
          if not request.POST.get('tos', None):
             form.errors.update({"rules": _("Agreement with terms is required")})


   if request.POST.get('Login', None):
       auth_form = AuthenticationForm(request, data=request.POST)
       if auth_form.is_valid():
          user = authenticate(email=request.POST.get("username", ""), password=request.POST.get("password", ""))
          login(request, user)
          try:
            cabinet = Cabinet.objects.get(user=user.pk)
          except ObjectDoesNotExist:
            cabinet = Cabinet(user=user, create_user=user)
            cabinet.save()




          return HttpResponseRedirect(request.GET.get('next', '/'))

   return  render_to_response("Registr/registr.html", locals(), context_instance=RequestContext(request),
                              context_instance=RequestContext(request))






def user_logout(request):
    logout(request)
    return HttpResponseRedirect("/")













