from django.shortcuts import render
from django.shortcuts import render_to_response, get_object_or_404
from appl.models import News, Category, Country, Product
from core.models import Value, Item, Attribute, Dictionary
from appl import func
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse

from django.conf import settings

def newsList(request, page=1):
    user = request.user

    page = page
    result = func.getItemsListWithPagination("News", "NAME", "Active_From", "DETAIL_TEXT", "IMAGE", page=page)
    newsList = result[0]
    page = result[1]
    paginator_range = func.getPaginatorRange(page)

    url_paginator = "news:paginator"

    hierarchyStructure = Category.hierarchy.getTree(siteID=settings.SITE_ID)
    categories_id = [cat['ID'] for cat in hierarchyStructure]
    categories = Item.getItemsAttributesValues(("NAME",), categories_id)
    categotySelect = func.setStructureForHiearhy(hierarchyStructure, categories)


    contrySorted = func.sortByAttr("Country", "NAME")
    sorted_id = [coun.id for coun in contrySorted]
    countryList = Item.getItemsAttributesValues(("NAME",), sorted_id)

    return render_to_response("News/index.html", locals())


def newsDetail(request, item_id):

    new = get_object_or_404(News, pk=item_id)
    user = request.user

    newAttr =  new.getAttributeValues("NAME", "ACTIVE_FROM", "DETAIL_TEXT", "IMAGE")
    newAttr = newAttr



    hierarchyStructure = Category.hierarchy.getTree(siteID=settings.SITE_ID)
    categories_id = [cat['ID'] for cat in hierarchyStructure]
    categories = Item.getItemsAttributesValues(("NAME",), categories_id)
    categotySelect = func.setStructureForHiearhy(hierarchyStructure, categories)


    contrySorted = func.sortByAttr("Country", "NAME")
    sorted_id = [coun.id for coun in contrySorted]
    countryList = Item.getItemsAttributesValues(("NAME",), sorted_id)

    products = Product.active.get_active_related().filter(sites=settings.SITE_ID).order_by("-pk")[:2]
    newProducrList = Product.getCategoryOfPRoducts(products, ("NAME", "COST", "CURRENCY", "IMAGE"))

    return render_to_response("News/detail.html", locals())


