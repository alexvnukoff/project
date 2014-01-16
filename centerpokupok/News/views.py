from django.shortcuts import render
from django.shortcuts import render_to_response
from appl.models import News
from core.models import Value, Item, Attribute, Dictionary
from appl import func
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist

from django.conf import settings

def newsList(request):
    page = request.GET.get('page', 1)
    result = func.getItemsListWithPagination("News", "NAME", "Active_From", "DETAIL_TEXT", "IMAGE", page=page)
    newsList = result[0]
    page = result[1]
    paginator_range = func.getPaginatorRange(page)
    flagList = func.getItemsList("Country", "NAME", "Flag")

    return render_to_response("News/index.html", locals())


def newsDetail(request, item_id):
    try:
      new = News.objects.get(pk=item_id)
    except ObjectDoesNotExist:
        raise Http404

    newAttr =  new.getAttributeValues("Name", "Active_From", "Detail_Text", "Photo")
    newAttr = newAttr
    flagList = func.getItemsList("Country", "NAME", "Flag")

    return render_to_response("News/detail.html", locals())


