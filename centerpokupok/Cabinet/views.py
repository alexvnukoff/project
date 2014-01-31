from django.shortcuts import render_to_response, get_object_or_404
from appl.models import News, Category, Country, Product, Cabinet, Order
from core.models import Value, Item, Attribute, Dictionary, User
from appl import func
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext
from centerpokupok.forms import UserDetail, OrderForm
from django.utils.translation import ugettext as _


@login_required(login_url=("/registration/"))
def get_profile(request):
    user = request.user
    curr_url = "main"
    succsefull_save = ""
    if request.POST:
        user_form = UserDetail(request.POST)
        if user_form.is_valid():
            user.first_name = user_form.cleaned_data['first_name']
            user.last_name = user_form.cleaned_data['last_name']
            user.date_of_birth = user_form.cleaned_data['birthday']
            user.save()
            succsefull_save = _("was successfully saved ")
    else:
        user_form = UserDetail(initial={"first_name": user.first_name, 'last_name': user.last_name,
                               "birthday": user.date_of_birth})


    return render_to_response("Cabinet/index.html", {'user_form': user_form, 'user': user,
                                                     'succsefull_save': succsefull_save, 'curr_url': curr_url},
                                                      context_instance=RequestContext(request))

@login_required(login_url=("/registration/"))
def get_shipping_detail(request):
    user = request.user
    succsefull_save = ""
    curr_url = "shipping_address"
    if request.POST:
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            cabinet = get_object_or_404(Cabinet, user=user.pk)
            cabinet.setAttributeValue({'CITY': [order_form.cleaned_data['city']],
                                       'COUNTRY': [order_form.cleaned_data['country']],
                                       'ZIP': [order_form.cleaned_data['zipcode']],
                                       'ADDRESS': [order_form.cleaned_data['address']],
                                       'TELEPHONE_NUMBER': [order_form.cleaned_data['telephone_number']],
                                       'SHIPPING_NAME': [order_form.cleaned_data['recipient_name']]}, user)
            succsefull_save = _("was successfully saved ")

    else:
        cabinet = get_object_or_404(Cabinet, user=user.pk)
        address = cabinet.getAttributeValues("CITY", "COUNTRY", "ZIP", "ADDRESS", "TELEPHONE_NUMBER", "SHIPPING_NAME")
        if not address:
            address = {}
        order_form = OrderForm(initial={'recipient_name': address['SHIPPING_NAME'][0] if address.get('SHIPPING_NAME', False) else "",
                                        'city': address['CITY'][0] if address.get('CITY', False) else "",
                                        'country': address['COUNTRY'][0] if address.get('COUNTRY', False) else "",
                                        'zipcode':address['ZIP'][0] if address.get('ZIP', False) else "",
                                        'address': address['ADDRESS'][0] if address.get('ADDRESS', False) else "",
                                        'telephone_number':address['TELEPHONE_NUMBER'][0] if address.get('TELEPHONE_NUMBER', False) else ""
                                        })


    return render_to_response("Cabinet/shippingAddress.html", {'order_form': order_form, 'user': user,
                                                               'succsefull_save': succsefull_save, 'curr_url': curr_url},
                                                                context_instance=RequestContext(request))

def get_order_history(request, page=1):

    hierarchyStructure = Category.hierarchy.getTree()
    categories_id = [cat['ID'] for cat in hierarchyStructure]
    categories = Item.getItemsAttributesValues(("NAME",), categories_id)
    categotySelect = func.setStructureForHiearhy(hierarchyStructure, categories)


    contrySorted = func.sortByAttr("Country", "NAME")
    sorted_id = [coun.id for coun in contrySorted]
    countryList = Item.getItemsAttributesValues(("NAME",), sorted_id)


    user = request.user
    curr_url = "order_history"
    cabinet = Cabinet.objects.filter(user=user)
    orders = Order.objects.filter(c2p__parent__in=cabinet).order_by("-pk")
    attr = ("IMAGE", 'NAME', 'CURRENCY', 'COST', 'QUANTITY', 'CITY', 'COUNTRY', 'ADDRESS')
    result = func.setPaginationForItemsWithValues(orders, *attr, page_num=5, page=page)
    orderList = result[0]
    page = result[1]
    paginator_range = func.getPaginatorRange(page)

    url_paginator = "profile:paginator"

    return render_to_response("Cabinet/orderHistory.html", {"user": user, 'curr_url': curr_url,
                                                            'categotySelect': categotySelect, 'countryList': countryList,
                                                            'orderList': orderList, 'paginator_range': paginator_range,
                                                            'url_paginator': url_paginator, 'page': page})















