from django.shortcuts import render_to_response
from appl.models import News
from core.models import Value, Item
from appl import func

# Create your views here.


def set_news_list(request):
    itemsList = func.getItemsList("News", "Detail Text", "Detail Picture")
    return render_to_response("NewsList.html",locals())