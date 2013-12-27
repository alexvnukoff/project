from django.shortcuts import render
from django.shortcuts import render_to_response
from appl.models import News, Basket, Tpp
from django.http import Http404
from core.models import Value, Item, Attribute, Dictionary, AttrTemplate
from appl import func

from django.db.models import get_app, get_models
from tppcenter.forms import ItemForm

from django.conf import settings

def home(request):
    id = settings.SITE_ID
    return render_to_response("home.html")

def set_news_list(request):
    page = request.GET.get('page', 1)
    result = func.getItemsListWithPagination("News", "Anons", "Text", "Image", page=page)

    itemsList = result[0]
    page = result[1]
    return render_to_response('NewsList.html', locals())


def set_items_list(request):
        app = get_app("appl")
        items = []
        for model in get_models(app):
            if issubclass(model, Item):
               items.append(model._meta.object_name)

        return render_to_response("items.html", locals())

def set_item_list(request, item):
    i = (globals()[item])
    if not issubclass(i, Item):
        raise Http404
    else:
        page = request.GET.get('page', 1)
        result = func.getItemsListWithPagination(item, "Anons", page=page)
        itemsList = result[0]
        page = result[1]
    return render_to_response('list.html', locals())


def get_item_form(request, item):
    form = ItemForm(initial=item)
    return render_to_response('forelement.html', locals())