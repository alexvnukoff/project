from django.shortcuts import render
from django.shortcuts import render_to_response
from appl.models import *
from django.http import Http404
from core.models import Value, Item, Attribute, Dictionary, AttrTemplate , Relationship
from appl import func
from django.core.exceptions import ValidationError
from django.forms.models import modelformset_factory
from django.db.models import get_app, get_models
from tppcenter.forms import ItemForm, Test, BasePhotoGallery
from django.template import RequestContext

from django.conf import settings

def home(request):
    id = settings.SITE_ID
    obj = Tpp.objects.get(title="Moscow Tpp")
    companies = obj.getItemList()
    i = companies
    return render_to_response("home.html")

def set_news_list(request):
    page = request.GET.get('page', 1)
    result = func.getItemsListWithPagination("News", "Name", "Detail_text", "Photo", page=page)

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

    item = item
    return render_to_response('list.html', locals())

def showlist(request, item, page):
    i = (globals()[item])
    if not issubclass(i, Item):
        raise Http404
    else:
        result = func.getItemsListWithPagination(item, "NAME", page=page)
        itemsList = result[0]
        page = result[1]
    return render_to_response('itemlist.html', locals())


def get_item(request, item):

    i = request.POST
    if not i:
        form = ItemForm(item)


    else:
        files = request.FILES
        post = request.POST
        values = {}
        values.update(files)
        values.update(post)
        form = ItemForm(item, values=values)
        form.clean()
        if form.is_valid():
            com = form.save()
           # obj = Tpp.objects.get(title="Moscow Tpp")
            #Relationship.objects.create(title=obj.name, parent=obj, child=com, create_user=request.user)
    return render_to_response('forelement.html', locals())


def get_item_form(request, item):

    i = request.POST
    if not i:
        form = ItemForm(item)


    else:
        files = request.FILES
        post = request.POST
        values = {}
        values.update(files)
        values.update(post)
        form = ItemForm(item, values=values)
        form.clean()
        if form.is_valid():
            com = form.save(request.user)






    return render_to_response('forelement.html', locals(), context_instance=RequestContext(request))

def update_item(request, item, id):

    i = request.POST
    if not i:
        form = ItemForm(item, id=id)
    else:
        files = request.FILES
        post = request.POST
        values = {}
        values.update(files)
        values.update(post)
        form = ItemForm(item, values=values, id=id)
        form.clean()
        if form.is_valid():
            com = form.save(request.user)




    return render_to_response('forelement.html', locals(), context_instance=RequestContext(request))


def meth(request):
    Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=2, fields=("photo", "title"))
    if not request.POST:
        form = Photo()
        itemform = ItemForm(item)
    else:
        form = Photo(request.POST, request.FILES)
        values = {}
        values.update(request.FILES)
        values.update(request.POST)
        itemform = ItemForm(item, values=values)
        itemform.clean()
        if form.is_valid():
            ob = itemform.save()
            form.save(parent=ob.id, user=request.user)
    return False








