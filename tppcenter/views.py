from django.shortcuts import render
from django.shortcuts import render_to_response
from appl.models import *
from django.http import Http404
from core.models import Value, Item, Attribute, Dictionary, AttrTemplate, Relationship
from appl import func
from django.core.exceptions import ValidationError
from django.forms.models import modelformset_factory
from django.db.models import get_app, get_models
from tppcenter.forms import ItemForm, Test, BasePhotoGallery
from django.template import RequestContext
from datetime import datetime
from django.utils.timezone import now

from django.conf import settings

def home(request):
    countries = Country.active.get_active()
    countries_id = [country.pk for country in countries]

    countriesList = Item.getItemsAttributesValues(("NAME", 'FLAG'), countries_id)

    organizations = Tpp.active.get_active().filter(p2c__child__in=Country.objects.all()).distinct()
    organizations_id = [organization.pk for organization in organizations]

    organizationsList = Item.getItemsAttributesValues(("NAME", 'FLAG'), organizations_id)

    products = Product.active.get_active_related()[:3]
    products = products.values('c2p__parent__organization__c2p__parent__country', "pk")
    country_dict = {}
    for product in products:
        country_dict[product['pk']] = product['c2p__parent__organization__c2p__parent__country']


    products_id = [product['pk'] for product in products]
    productsList = Item.getItemsAttributesValues(("NAME", 'IMAGE'), products_id)

    for id, product in productsList.items():
        toUpdate = {'COUNTRY_NAME': countriesList[country_dict[id]]['NAME'],
                   'COUNTRY_ID:': country_dict[id],
                   'COUNTRY_FLAG': countriesList[country_dict[id]]['FLAG']}
        product.update(toUpdate)


    services = Service.active.get_active_related()[:3]
    services = services.values('c2p__parent__organization__c2p__parent__country', 'c2p__parent__organization', "pk")
    services_dict = {}
    for service in services:
        services_dict[service['pk']] = {}
        services_dict[service['pk']]['country'] = service['c2p__parent__organization__c2p__parent__country']
        services_dict[service['pk']]['company'] = service['c2p__parent__organization']

    services_id = [service['pk'] for service in services]
    serviceList = Item.getItemsAttributesValues(("NAME",), services_id)
    companies_id = [service['c2p__parent__organization'] for service in services]
    companyList = Item.getItemsAttributesValues(("NAME",), companies_id)

    for id, service in serviceList.items():
        toUpdate = {'COUNTRY_NAME': countriesList[services_dict[id]['country']]['NAME'],
                   'COUNTRY_ID':  services_dict[id]['country'],
                   'COUNTRY_FLAG':  countriesList[services_dict[id]['country']]['FLAG'],
                   'COMPANY_NAME': companyList[services_dict[id]['company']]['NAME'],
                   'COMPANY_ID': services_dict[id]['company']}
        service.update(toUpdate)

    greetings = Greeting.active.get_active().all()
    greetings_id = [greeting.id for greeting in greetings]
    greetingsList = Item.getItemsAttributesValues(("TPP", 'IMAGE', 'AUTHOR_NAME', "POSITION"), greetings_id)

    exhibitions = Exhibition.active.get_active_related()[:3]
    exhibitions = exhibitions.values('c2p__parent__organization', "pk")
    exhibitions_id = [exhibition['pk'] for exhibition in exhibitions]
    exhibitions_dict = {}
    for exhibition in exhibitions:
        exhibitions_dict[exhibition['pk']] = exhibition['c2p__parent__organization']

    exhibitionsList = Item.getItemsAttributesValues(("NAME", 'CITY', 'COUNTRY', "EVENT_DATE"), exhibitions_id)

    for id, exhibition in exhibitionsList.items():
        toUpdate = {'ORG_NAME': organizationsList[exhibitions_dict[id]]['NAME'],
                    'ORG_FLAG': organizationsList[exhibitions_dict[id]]['FLAG'],
                    'ORG_ID': exhibitions_dict[id]}
        exhibition.update(toUpdate)






    return render_to_response("index.html", {"countriesList": countriesList, 'organizationsList': organizationsList,
                                             'productsList': productsList, 'serviceList': serviceList,
                                             'greetingsList': greetingsList, 'exhibitionsList': exhibitionsList})

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

def test(request):
    '''
        import uuid
        from django.utils.timezone import now
        a = Company(create_user=request.user)
        a.save()

        from core.tasks import add
        i = now()
        name = uuid.uuid4()
        tnow = "%s/%s/%s" % (i.day, i.month, i.year)

        add.delay(a.pk, request.user, {'NAME': 'Company Test'},
                    'C:\\Users\\user\\PycharmProjects\\tpp\\appl\Static\pr5.jpg')
    '''



    return render_to_response('test.html', locals(), context_instance=RequestContext(request))


def test2(request):


    return HttpResponse(z)




