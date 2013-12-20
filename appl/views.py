from itertools import count
from django.shortcuts import render_to_response
from appl.models import News
from core.models import Value, Item
from appl import func


def set_news_list(request):
    page = request.GET.get('page',1)
    result = func.getItemsListWithPagination("News", "Detail Text", "Detail Picture", page=page)
    itemsList = result[0]
    page = result[1]
    return render_to_response('NewsList.html',locals())