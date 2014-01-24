from django.shortcuts import render
from django.shortcuts import render_to_response
from appl.models import News
from core.models import Value, Item, Attribute, Dictionary
from appl import func
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse

from django.conf import settings

def newsList(request, page=1):
    page = page
    result = func.getItemsListWithPagination("News", "NAME", "Active_From", "DETAIL_TEXT", "IMAGE", page=page)
    newsList = result[0]
    page = result[1]
    paginator_range = func.getPaginatorRange(page)
    flagList = func.getItemsList("Country", "NAME", "FLAG")
    url_paginator = "news:paginator"

    return render_to_response("News/index.html", locals())


def newsDetail(request, item_id):
    try:
      new = News.objects.get(pk=item_id)
    except ObjectDoesNotExist:
        raise Http404

    newAttr =  new.getAttributeValues("NAME", "ACTIVE_FROM", "DETAIL_TEXT", "IMAGE")
    newAttr = newAttr
    flagList = func.getItemsList("Country", "NAME", "FLAG")

    return render_to_response("News/detail.html", locals())


