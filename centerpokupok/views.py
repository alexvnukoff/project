from datetime import datetime

from django.shortcuts import render_to_response
from django.template import RequestContext
from haystack.backends import SQ
from registration.backends.default.views import RegistrationView
from registration.forms import RegistrationFormUniqueEmail
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _
from django.conf import settings

from appl.models import Category, Product, Cabinet
from core.models import Item
from appl import func


def home(request, country=None):


    products = func.getActiveSQS().models(Product).filter(sites=settings.SITE_ID).order_by("-obj_create_date")[:4]

    #----NEW PRODUCT LIST -----#
    if country:
        products = products.filter(country=country)


    newProducrList = func.get_categories_data_for_products(products)

    #----NEW PRODUCT LIST -----#
    if not country:
        products = func.getActiveSQS().models(Product).filter(sites=settings.SITE_ID).order_by("-obj_create_date")[:4]
        products = [product.pk for product in products]
    else:
        productQuery = Product.active.get_active_related().filter(sites=settings.SITE_ID).order_by("-pk")
        products = Product.getTopSales(productQuery)[:4]
        products = [product.pk for product in products]

    topPoductList = func.getActiveSQS().models(Product).filter(django_id__in=products)

     #----MAIN MENU AND CATEGORIES IN HEADER ------#
    hierarchyStructure = Category.hierarchy.getTree(siteID=settings.SITE_ID)
    categories_id = [cat['ID'] for cat in hierarchyStructure]
    categories = Item.getItemsAttributesValues(("NAME",), categories_id)


    sortedHierarchyStructure = _sortMenu(hierarchyStructure) if len(hierarchyStructure) > 0 else {}
    level = 0
    for node in sortedHierarchyStructure:
        node['pre_level'] = level
        node['item'] = categories[node['ID']]
        node['parent_item'] = categories[node['PARENT_ID']] if node['PARENT_ID'] is not None else ""
        level = node['LEVEL']


    #get 3 active coupons ordered by end date
    #---------COUPONS----------#
    couponsObj = func.getActiveSQS().models(Product).filter(sites=settings.SITE_ID,
                                                                  coupon_start__lte=datetime.now(),
                                                                  coupon_end__gte=datetime.now()).order_by("coupon_end")[:3]

    if country:
        couponsObj = couponsObj.filter(country=country)


    #----------- Products with discount -------------#

    productsSale = func.getActiveSQS().models(Product).filter(SQ(coupon=0) | SQ(coupon_end__lt=datetime.now()),
                                                    sites=settings.SITE_ID, discount__gt=0).order_by("-discount")[:15]

    if country:
          productsSale = productsSale.filter(country=country)


    url_country = "home_country"

    user = request.user

    return render_to_response("index.html", {'sortedHierarchyStructure': sortedHierarchyStructure,
                                             'coupons': couponsObj, "newProducrList": newProducrList,
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

   return  render_to_response("Registr/registr.html", locals(), context_instance=RequestContext(request))







def user_logout(request):
    logout(request)
    return HttpResponseRedirect("/")













