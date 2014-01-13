from django.shortcuts import render
from django.shortcuts import render_to_response
from appl.models import News
from core.models import Value, Item, Attribute, Dictionary
from appl import func

from django.conf import settings

def home(request):
    newsList = func.getItemsList("News", "Name", "Active_From", "Photo", qty=3)
    return render_to_response("index.html", locals())

def about(request):

    return render_to_response("About/About.html")

def set_news_list(request):
    page = request.GET.get('page', 1)
    result = func.getItemsListWithPagination("News", "Anons", "Text", "Image", page=page)

    itemsList = result[0]
    page = result[1]
    return render_to_response('NewsList.html', locals())

