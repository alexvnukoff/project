from itertools import count
from django.shortcuts import render_to_response
from appl.models import News
from core.models import Value, Item, Attribute ,Dictionary
from appl import func


def set_news_list(request):
    #dict = Dictionary.objects.get(title="Sex")
    #dict.deleteSlot("Jopa")








    page = request.GET.get('page', 1)
    result = func.getItemsListWithPagination("News", "Detail_Text", "Detail_Picture","Anonce_Text", page=page)

    itemsList = result[0]
    page = result[1]
    return render_to_response('NewsList.html',locals())