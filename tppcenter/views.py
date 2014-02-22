from django.shortcuts import render
from django.shortcuts import render_to_response
from appl.models import *
from django.http import Http404, HttpResponse, HttpResponseRedirect
from core.models import Value, Item, Attribute, Dictionary, AttrTemplate, Relationship, Slot
from appl import func
from django.core.exceptions import ValidationError
from django.forms.models import modelformset_factory
from django.db.models import get_app, get_models
from tppcenter.forms import ItemForm, Test, BasePhotoGallery
from django.template import RequestContext, loader
from django.views.decorators.csrf import ensure_csrf_cookie
from datetime import datetime
from django.views.decorators.cache import cache_page
from django.utils.timezone import now
from registration.forms import RegistrationFormUniqueEmail
from django.contrib.auth.forms import AuthenticationForm
from registration.backends.default.views import RegistrationView
from django.utils.translation import ugettext as _
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse

from django.conf import settings

def home(request):



    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('news:main'))

    if request.POST.get('Register', None):
        return registration(request)

    countries = Country.active.get_active()
    countries_id = [country.pk for country in countries]

    countriesList = Item.getItemsAttributesValues(("NAME", 'FLAG'), countries_id)

    organizations = Tpp.active.get_active().filter(c2p__parent__in=Country.objects.all()).distinct()
    organizations_id = [organization.pk for organization in organizations]

    organizationsList = Item.getItemsAttributesValues(("NAME", 'FLAG'), organizations_id)

    products = Product.active.get_active_related().order_by('-pk')[:3]
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
                                             'greetingsList': greetingsList, 'exhibitionsList': exhibitionsList},

                              context_instance=RequestContext(request))
@ensure_csrf_cookie
def getNotifList(request):
    if request.is_ajax():
        notifications = Notification.objects.filter(user=request.user, read=False).order_by("-pk")[:3]
        messages_id = [notification.message.pk for notification in notifications]
        notifications_id = [notification.pk for notification in notifications]





        notificationsValues = Item.getItemsAttributesValues(('DETAIL_TEXT',), messages_id)
        notifDict = {}

        for notification in notifications:
            notifDict[notification.pk] = notificationsValues[notification.message.pk]

        Notification.objects.filter(pk__in=notifications_id)  .update(read=True)


        template = loader.get_template('main/notoficationlist.html')
        context = RequestContext(request, {'notifDict': notifDict})

        return HttpResponse(template.render(context))


def user_login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('news:main'))

    form = None
    if request.POST.get('Login', None):
       form = AuthenticationForm(request, data=request.POST)
       if form.is_valid():
          user = authenticate(email=request.POST.get("username", ""), password=request.POST.get("password", ""))
          login(request, user)
          return HttpResponseRedirect(reverse('news:main'))

    return render_to_response("registration/login.html", {'form': form}, context_instance=RequestContext(request))



def user_logout(request):
    logout(request)
    return HttpResponseRedirect("/")

def registration(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('news:main'))

    if request.POST.get('Register', None):
         form = RegistrationFormUniqueEmail(request.POST)
         if form.is_valid() and request.POST.get('tos', None):
            cleaned = form.cleaned_data
            reg_view = RegistrationView()
            try:
                reg_view.register(request, **cleaned)
                return render_to_response("registration/registration_complete.html", locals())
            except ValueError:
                return render_to_response("registration/registration_closed.html")
         else:
              if not request.POST.get('tos', None):
                 form.errors.update({"rules": _("Agreement with terms is required")})
              return render_to_response('registration/registration.html', {'form': form, 'user': request.user}, context_instance=RequestContext(request))

    return render_to_response('registration/registration.html', {'user': request.user}, context_instance=RequestContext(request))













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
            com = form.save(request.user, settings.SITE_ID)
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
            com = form.save(request.user, settings.SITE_ID)






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
            com = form.save(request.user, settings.SITE_ID)




    return render_to_response('forelement.html', locals(), context_instance=RequestContext(request))


def meth(request):
    Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=2, fields=("photo", "title"))
    if not request.POST:
        form = Photo()
        itemform = ItemForm(Item)
    else:
        form = Photo(request.POST, request.FILES)
        values = {}
        values.update(request.FILES)
        values.update(request.POST)
        itemform = ItemForm(Item, values=values)
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


def ping(request):
    from django.http import StreamingHttpResponse


    return StreamingHttpResponse('pong')




