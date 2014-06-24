from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext, loader
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.forms.models import modelformset_factory
from django.db.models import get_app, get_models
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect, csrf_exempt
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.translation import ugettext as _
from registration.backends.default.views import RegistrationView
from registration.forms import RegistrationFormUniqueEmail
from appl.models import Country, Organization, Branch, Category, Company, Tpp, Gallery, Cabinet, Notification, \
    Exhibition, Greeting, BusinessProposal, Product, ExternalSiteTemplate, BpCategories
from tppcenter.forms import ItemForm, BasePhotoGallery
from appl import func
from core.models import Item, User
from collections import OrderedDict
from django.core.mail import send_mail
import json

@csrf_protect
def home(request):

    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('wall:main'))

    if request.POST.get('Register', None):
        return registration(request)

    cache_name = 'home_page'
    cached = cache.get(cache_name)

    if not cached:

        organizations = Tpp.active.get_active().filter(p2c__child__in=Country.objects.all()).distinct()
        organizations_id = [organization.pk for organization in organizations]

        organizationsList = Item.getItemsAttributesValues(("NAME", 'FLAG', 'SLUG', 'TITLE_DESCRIPTION'), organizations_id)

        products = Product.active.get_active().order_by('-pk')[:3]

        products_id = [product.pk for product in products]
        productsList = Item.getItemsAttributesValues(("NAME", 'IMAGE', 'SLUG'), products_id)
        func.addDictinoryWithCountryAndOrganization(products_id, productsList)

        services = BusinessProposal.active.get_active().order_by('-pk')[:3]

        services_id = [service.id for service in services]
        serviceList = Item.getItemsAttributesValues(("NAME", 'SLUG'), services_id)
        func.addDictinoryWithCountryAndOrganization(services_id, serviceList)



        greetings = Greeting.active.get_active().all()
        greetings_id = [greeting.id for greeting in greetings]
        greetingsList = Item.getItemsAttributesValues(("TPP", 'IMAGE', 'AUTHOR_NAME', "POSITION", "SLUG"), greetings_id)

        exhibitions = Exhibition.active.get_active().order_by("-pk")[:3]
        exhibitions_id = [exhibition.pk for exhibition in exhibitions]
        exhibitionsList = Item.getItemsAttributesValues(("NAME", 'CITY', 'COUNTRY', "START_EVENT_DATE", 'SLUG'), exhibitions_id)
        func.addDictinoryWithCountryAndOrganization(exhibitions_id, exhibitionsList)

        templateParams = {
            'organizationsList': organizationsList,
            'productsList': productsList,
            'serviceList': serviceList,
            'greetingsList': greetingsList,
            'exhibitionsList': exhibitionsList,
        }



        cache.set(cache_name, templateParams)
    else:
        templateParams = cache.get(cache_name)

    template = loader.get_template('index.html')
    context = RequestContext(request, templateParams)
    rendered = template.render(context)


    return HttpResponse(rendered)


@ensure_csrf_cookie
@login_required(login_url='/login/')
def getNotifList(request):


    if request.is_ajax():

        #Older notifications
        last = int(request.GET.get('last', 0))

        #New notifications
        first = int(request.GET.get('first', 0))

        #Disable loading of empty list
        lastLine = False

        notifications = Notification.objects.filter(user=request.user).select_related('message__pk')

        if last != 0:
            notifications = notifications.filter(pk__lt=last).order_by("-pk")[:3]

            if len(notifications) < 3:
                lastLine = True

        elif first != 0:
            notifications = notifications.filter(pk__gt=first).order_by("-pk")[:20]
        else:
            notifications = notifications.order_by("-pk")[:3]


        messages_id = [notification.message.pk for notification in notifications]
        notifications_id = [notification.pk for notification in notifications]

        notificationsValues = Item.getItemsAttributesValues(('DETAIL_TEXT',), messages_id)
        notifDict = OrderedDict()

        for notification in notifications:
            notifDict[notification.pk] = notificationsValues[notification.message.pk]

        unread = Notification.objects.filter(pk__in=notifications_id, read=False)

        unreadCount = unread.count()
        unread.update(read=True)

        template = loader.get_template('main/notoficationlist.html')
        context = RequestContext(request, {'notifDict': notifDict, 'lastLine': lastLine})
        data = template.render(context)

        return HttpResponse(json.dumps({'data': data, 'count': unreadCount}))
    else:
        return HttpResponseBadRequest()



@ensure_csrf_cookie
def registerToExebition(request):


    if request.is_ajax() and request.POST.get('NAME', False) and request.POST.get('EMAIL', False):

        adminEmail = 'admin@tppcenter.com'
        companyEmail = request.POST.get('SEND_EMAIL', None)

        message_name = _('%(name)s , was registered to your event %(event)s ,') % {"name": request.POST.get('NAME'), "event" : request.POST.get('EXEBITION', "")}
        message_company = (_('working in the %(company)s ') % {'company': request.POST.get('COMPANY')}) if request.POST.get('COMPANY', False) else ""
        message_position = (_('on the position of %(position)s . ') % {'position': request.POST.get('POSITION')}) if request.POST.get('POSITION', False) else ""
        message_email = _('You can contact him at this email address %(email)s  ') % {"email": request.POST.get('EMAIL')}
        message = (message_name + message_company + message_position + message_email)

        send_mail(_('Registartion to event'), message, 'noreply@tppcenter.com',
                            [adminEmail], fail_silently=False)
        if companyEmail:
            send_mail(_('Registartion to event'), message, 'noreply@tppcenter.com',
                            [companyEmail], fail_silently=False)


    return HttpResponse("")



def user_login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('news:main'))

    form = None

    if request.POST.get('Login', None):
       form = AuthenticationForm(request, data=request.POST)

       if form.is_valid():
          user = authenticate(email=request.POST.get("username", ""), password=request.POST.get("password", ""))
          login(request, user)
          if user.is_authenticated():
               cabinet, created = Cabinet.objects.get_or_create(user=user, create_user=user)

               if created:
                   group = Group.objects.get(name='Company Creator')
                   user.is_manager = True
                   user.save()
                   group.user_set.add(user)
                   cabinet.reindexItem()
                   return HttpResponseRedirect(reverse('profile:main'))

               else:
                   return HttpResponseRedirect(reverse('wall:main'))

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
    if not request.user.is_superuser:
        raise PermissionError
    page = request.GET.get('page', 1)
    result = func.getItemsListWithPagination("News", "Name", "Detail_text", "Photo", page=page)

    itemsList = result[0]

    page = result[1]
    return render_to_response('NewsList.html', locals())


def set_items_list(request):
        if not request.user.is_superuser:
            raise PermissionError
        app = get_app("appl")
        items = []

        for model in get_models(app):
            if issubclass(model, Item):
               items.append(model._meta.object_name)

        return render_to_response("items.html", locals())

def set_item_list(request, item):
    if not request.user.is_superuser:
        raise PermissionError

    item = item
    return render_to_response('list.html', locals())

def showlist(request, item, page):
    if not request.user.is_superuser:
        raise PermissionError
    i = (globals()[item])

    if not issubclass(i, Item):
        raise Http404
    else:
        result = func.getItemsListWithPagination(item, "NAME", page=page)
        itemsList = result[0]
        page = result[1]
    return render_to_response('itemlist.html', locals())


def get_item(request, item):

    if not request.user.is_superuser:
        raise PermissionError

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
    if not request.user.is_superuser:
        raise PermissionError

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
    if not request.user.is_superuser:
        raise PermissionError

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
    if not request.user.is_superuser:
        raise PermissionError
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


def jsonFilter(request):
    import json

    filter = request.GET.get('type', None)
    q = request.GET.get('q', None)
    page = request.GET.get('page', None)


    if request.is_ajax() and type and page and (len(q) == 0 or len(q) > 2):
        from haystack.query import SearchQuerySet
        from django.core.paginator import Paginator

        model = None


        if filter == 'tpp':
            model = Tpp
        elif filter == "company":
            model = Company
        elif filter == "category":
            model = Category
        elif filter == "branch":
            model = Branch
        elif filter == 'country':
            model = Country
        elif filter == 'bp_category':
            model = BpCategories

        if model:

            if not q:
                sqs = SearchQuerySet().models(model).order_by('title_sort')
            else:
                sqs = SearchQuerySet().models(model).autocomplete(title_auto=q).order_by('title_sort')

            paginator = Paginator(sqs, 10)
            total = paginator.count

            try:
                onPage = paginator.page(page)
            except Exception:
                onPage = paginator.page(1)

            items = [{'title': item.title_auto, 'id': item.id} for item in onPage.object_list]

            return HttpResponse(json.dumps({'content': items, 'total': total}))

    return HttpResponse(json.dumps({'content': [], 'total': 0}))

def test(request):
    a = func.getAnalytic({'dimensions': 'ga:dimension2'})

    return HttpResponse(a)

def getLiveTop(request):

    filterAdv = func.getListAdv(request)

    templateParams = {
        'MEDIA_URL': settings.MEDIA_URL,
        'modelTop': func.getTops(request, filterAdv)
    }

    return render_to_response("AdvTop/tops.html", templateParams)

def getLiveBanner(request):

    filterAdv = func.getListAdv(request)

    places = request.POST.getlist('places[]', [])

    templateParams = {
        'MEDIA_URL': settings.MEDIA_URL,
        'banners': func.getBanners(places, settings.SITE_ID, filterAdv)
    }

    return render_to_response("AdvBanner/banners.html", templateParams)

def ping(request):
    from django.http import StreamingHttpResponse


    return StreamingHttpResponse('pong')


def getAdditionalPage(request):
    i = request.GET.get('NUMBER', "")

    template = loader.get_template('additionalPage.html')
    context = RequestContext(request, {'i': i})

    return HttpResponse(template.render(context))


def perm_denied(request):
    template = loader.get_template('permissionDen.html')
    context = RequestContext(request)

    return render_to_response("main/denied.html", {'DeniedContent': template.render(context)},
                              context_instance=RequestContext(request))

def redirectTo(request, to):
    from django.shortcuts import redirect

    return redirect('http://archive.tppcenter.com/' + to, permanent=True)


def setCurrent(request, item_id):

    if item_id != '0':
        try:
            item = Organization.objects.get(pk=item_id)
        except ObjectDoesNotExist:
            return HttpResponseRedirect(reverse('denied'))

        perm_list = item.getItemInstPermList(request.user)

        if 'change_company' not in perm_list and 'change_tpp' not in perm_list:
            return HttpResponseRedirect(reverse('denied'))

        current_company = int(item_id)
    else:
        current_company = False

    request.session['current_company'] = current_company


    return HttpResponseRedirect(request.GET.get('next'), '/')

def buildCountries(request):
    if not request.user.is_superuser:
        raise PermissionError('you have not enough permissions')

    crt_usr = User.objects.get(pk=1)
    countries = {'Azerbaydjan': {'NAME': {'title': 'Azerbaydjan', 'title_ru': 'Азербайджан', "title_en": "Azerbaydjan"}, 'COUNTRY_FLAG': "sprite-flag_azerbaijan"},
                 'Armenia': {'NAME': {'title': 'Armenia', 'title_ru': 'Армения', "title_en": "Armenia"}, 'COUNTRY_FLAG': "sprite-flag_armenia"},
                 'Belarus': {'NAME': {'title': 'Belarus', 'title_ru': 'Беларусь', "title_en": "Belarus"}, 'COUNTRY_FLAG': "sprite-flag_belarus"},
                 'Georgia': {'NAME': {'title': 'Georgia', 'title_ru': 'Грузия', "title_en": "Georgia"}, 'COUNTRY_FLAG': "sprite-flag_georgia"},
                 'Israel': {'NAME': {'title': 'Israel', 'title_ru': 'Израиль', "title_en": "Israel"}, 'COUNTRY_FLAG': "sprite-flag_israel"},
                 'Kazakhstan': {'NAME': {'title': 'Kazakhstan', 'title_ru': 'Казахстан', "title_en": "Kazakhstan"}, 'COUNTRY_FLAG': "sprite-flag_kazakhstan"},
                 'Kyrgyzstan': {'NAME': {'title': 'Kyrgyzstan', 'title_ru': 'Киргизия', "title_en": "Kyrgyzstan"}, 'COUNTRY_FLAG': "sprite-flag_kyrgyzstan"},
                 'Latvia': {'NAME': {'title': 'Latvia', 'title_ru': 'Латвия', "title_en": "Latvia"}, 'COUNTRY_FLAG': "sprite-flag_lithuania"},
                 'Lithuania': {'NAME': {'title': 'Lithuania', 'title_ru': 'Литва', "title_en": "Lithuania"}, 'COUNTRY_FLAG': "sprite-flag_lithuania"},
                 'Moldova': {'NAME': {'title': 'Moldova', 'title_ru': 'Молдова', "title_en": "Moldova"}, 'COUNTRY_FLAG': "sprite-flag_moldova"},
                 'Russia': {'NAME': {'title': 'Russia', 'title_ru': 'Россия', "title_en": "Russia"}, 'COUNTRY_FLAG': "sprite-flag_russia"},
                 'Tajikistan': {'NAME': {'title': 'Tajikistan', 'title_ru': 'Таджикистан', "title_en": "Tajikistan"}, 'COUNTRY_FLAG': "sprite-flag_tajikistan"},
                 'Turkmenistan': {'NAME': {'title': 'Turkmenistan', 'title_ru': 'Туркмения', "title_en": "Turkmenistan"}, 'COUNTRY_FLAG': "sprite-flag_turkmenistan"},
                 'Uzbekistan': {'NAME': {'title': 'Uzbekistan', 'title_ru': 'Узбекистан', "title_en": "Uzbekistan"}, 'COUNTRY_FLAG': "sprite-flag_uzbekistan"},
                 'Ukraine': {'NAME': {'title': 'Ukraine', 'title_ru': 'Украина', "title_en": "Ukraine"}, 'COUNTRY_FLAG': "sprite-flag_ukraine"},
                 'Estonia': {'NAME': {'title': 'Estonia', 'title_ru': 'Эстония', "title_en": "Estonia"}, 'COUNTRY_FLAG': "sprite-flag_estonia"},
                 'Afghanistan': {'NAME': {'title': 'Afghanistan', 'title_ru': 'Афганистан', "title_en": "Afghanistan"}, 'COUNTRY_FLAG': "sprite-flag_afghanistan"},
                 'Albania': {'NAME': {'title': 'Albania', 'title_ru': 'Албания', "title_en": "Albania"}, 'COUNTRY_FLAG': "sprite-flag_albania"},
                 'Algeria': {'NAME': {'title': 'Algeria', 'title_ru': 'Алжир', "title_en": "Algeria"}, 'COUNTRY_FLAG': "sprite-flag_algeria"},
                 'Andorra': {'NAME': {'title': 'Andorra', 'title_ru': 'Андорра', "title_en": "Andorra"}, 'COUNTRY_FLAG': "sprite-flag_andorra"},
                 'Angola': {'NAME': {'title': 'Angola', 'title_ru': 'Ангола', "title_en": "Angola"}, 'COUNTRY_FLAG': "sprite-flag_angola"},
                 'Antigua and Barbuda': {'NAME': {'title': 'Antigua and Barbuda', 'title_ru': 'Антигуа и Барбуда', "title_en": "Antigua and Barbuda"}, 'COUNTRY_FLAG': "sprite-flag_antigua_and_barbuda"},
                 'Argentina': {'NAME': {'title': 'Argentina', 'title_ru': 'Аргентина', "title_en": "Argentina"}, 'COUNTRY_FLAG': "sprite-flag_argentina"},
                 'Australia': {'NAME': {'title': 'Australia', 'title_ru': 'Австралия', "title_en": "Australia"}, 'COUNTRY_FLAG': "sprite-flag_australia"},
                 'Austria': {'NAME': {'title': 'Austria', 'title_ru': 'Австрия', "title_en": "Austria"}, 'COUNTRY_FLAG': "sprite-flag_austria"},
                 'Bahamas': {'NAME': {'title': 'Bahamas', 'title_ru': 'Багамские острова', "title_en": "Bahamas"}, 'COUNTRY_FLAG': "sprite-flag_bahamas"},
                 'Bahrain': {'NAME': {'title': 'Bahrain', 'title_ru': 'Бахрейн', "title_en": "Bahrain"}, 'COUNTRY_FLAG': "sprite-flag_bahrain"},
                 'Bangladesh': {'NAME': {'title': 'Bangladesh', 'title_ru': 'Бангладеш', "title_en": "Bangladesh"}, 'COUNTRY_FLAG': "sprite-flag_bangladesh"},
                 'Barbados': {'NAME': {'title': 'Barbados', 'title_ru': 'Барбадос', "title_en": "Barbados"}, 'COUNTRY_FLAG': "sprite-flag_barbados"},
                 'Belgium': {'NAME': {'title': 'Belgium', 'title_ru': 'Бельгия', "title_en": "Belgium"}, 'COUNTRY_FLAG': "sprite-flag_belgium"},
                 'Belize': {'NAME': {'title': 'Belize', 'title_ru': 'Белиз', "title_en": "Belize"}, 'COUNTRY_FLAG': "sprite-flag_belize"},
                 'Benin': {'NAME': {'title': 'Benin', 'title_ru': 'Бенин', "title_en": "Benin"}, 'COUNTRY_FLAG': "sprite-flag_benin"},
                 'Bhutan': {'NAME': {'title': 'Bhutan', 'title_ru': 'Бутан', "title_en": "Bhutan"}, 'COUNTRY_FLAG': "sprite-flag_bhutan"},
                 'Bolivia': {'NAME': {'title': 'Bolivia', 'title_ru': 'Боливия', "title_en": "Bolivia"}, 'COUNTRY_FLAG': "sprite-flag_bolivia"},
                 'Bosnia and Herzegovina': {'NAME': {'title': 'Bosnia and Herzegovina', 'title_ru': 'Босния и Герцеговина', "title_en": "Bosnia and Herzegovina"}, 'COUNTRY_FLAG': "sprite-flag_bosnia_and_herzegovina"},
                 'Botswana': {'NAME': {'title': 'Botswana', 'title_ru': 'Ботсвана', "title_en": "Botswana"}, 'COUNTRY_FLAG': "sprite-flag_botswana"},
                 'Brazil': {'NAME': {'title': 'Brazil', 'title_ru': 'Бразилия', "title_en": "Brazil"}, 'COUNTRY_FLAG': "sprite-flag_brazil"},
                 'Brunei': {'NAME': {'title': 'Brunei', 'title_ru': 'Бруней', "title_en": "Brunei"}, 'COUNTRY_FLAG': "sprite-flag_brunei"},
                 'Bulgaria': {'NAME': {'title': 'Bulgaria', 'title_ru': 'Болгария', "title_en": "Bulgaria"}, 'COUNTRY_FLAG': "sprite-flag_bulgaria"},
                 'Burkina Faso': {'NAME': {'title': 'Burkina Faso', 'title_ru': 'Буркина-Фасо', "title_en": "Burkina Faso"}, 'COUNTRY_FLAG': "sprite-flag_burkina_faso"},
                 'Burundi': {'NAME': {'title': 'Burundi', 'title_ru': 'Бурунди', "title_en": "Burundi"}, 'COUNTRY_FLAG': "sprite-flag_burundi"},
                 'Cambodia': {'NAME': {'title': 'Cambodia', 'title_ru': 'Камбоджа', "title_en": "Cambodia"}, 'COUNTRY_FLAG': "sprite-flag_cambodia"},
                 'Cameroon': {'NAME': {'title': 'Cameroon', 'title_ru': 'Камерун', "title_en": "Cameroon"}, 'COUNTRY_FLAG': "sprite-flag_cameroon"},
                 'Canada': {'NAME': {'title': 'Canada', 'title_ru': 'Канада', "title_en": "Canada"}, 'COUNTRY_FLAG': "sprite-flag_canada"},
                 'Cape Verde': {'NAME': {'title': 'Cape Verde', 'title_ru': 'Кабо-Верде', "title_en": "Cape Verde"}, 'COUNTRY_FLAG': "sprite-flag_cape_verde"},
                 'Central African Republic': {'NAME': {'title': 'Central African Republic', 'title_ru': 'Центрально-Африканская Республика', "title_en": "Central African Republic"}, 'COUNTRY_FLAG': "sprite-flag_central_african_republic"},
                 'Chad': {'NAME': {'title': 'Chad', 'title_ru': 'Чад', "title_en": "Chad"}, 'COUNTRY_FLAG': "sprite-flag_chad"},
                 'Chile': {'NAME': {'title': 'Chile', 'title_ru': 'Чили', "title_en": "Chile"}, 'COUNTRY_FLAG': "sprite-flag_chile"},
                 'China': {'NAME': {'title': 'China', 'title_ru': 'Китай', "title_en": "China"}, 'COUNTRY_FLAG': "sprite-flag_china"},
                 'Columbia': {'NAME': {'title': 'Columbia', 'title_ru': 'Колумбия', "title_en": "Columbia"}, 'COUNTRY_FLAG': "sprite-flag_colombia"},
                 'Comoros': {'NAME': {'title': 'Comoros', 'title_ru': 'Коморские острова', "title_en": "Comoros"}, 'COUNTRY_FLAG': "sprite-flag_comoros"},
                 'Democratic Republic of Congo': {'NAME': {'title': 'Democratic Republic of Congo', 'title_ru': 'Демократическая Республика Конго', "title_en": "Democratic Republic of Congo"}, 'COUNTRY_FLAG': "sprite-flag_congo_democratic_republic"},
                 'Congo Republic': {'NAME': {'title': 'Congo Republic', 'title_ru': 'Республика Конго', "title_en": "Congo Republic"}, 'COUNTRY_FLAG': "sprite-flag_congo_republic"},
                 'Cook Island': {'NAME': {'title': 'Cook Island', 'title_ru': 'острова Кука', "title_en": "Cook Island"}, 'COUNTRY_FLAG': "sprite-flag_cook_islands"},
                 'Costa Rica': {'NAME': {'title': 'Costa Rica', 'title_ru': 'Коста-Рика', "title_en": "Costa Rica"}, 'COUNTRY_FLAG': "sprite-flag_costa_rica"},
                 "Cote D'ivoire": {'NAME': {'title': "Cote D'ivoire", 'title_ru': 'Берег Слоновой Кости', "title_en": "Cote D'ivoire"}, 'COUNTRY_FLAG': "sprite-flag_cote_divoire"},
                 'Croatia': {'NAME': {'title': 'Croatia', 'title_ru': 'Хорватия', "title_en": "Croatia"}, 'COUNTRY_FLAG': "sprite-flag_croatia"},
                 'Cuba': {'NAME': {'title': 'Cuba', 'title_ru': 'Куба', "title_en": "Cuba"}, 'COUNTRY_FLAG': "sprite-flag_cuba"},
                 'Cyprus': {'NAME': {'title': 'Cyprus', 'title_ru': 'Кипр', "title_en": "Cyprus"}, 'COUNTRY_FLAG': "sprite-flag_cyprus"},
                 'Czech Republic': {'NAME': {'title': 'Czech Republic', 'title_ru': 'Чешская республика', "title_en": "Czech Republic"}, 'COUNTRY_FLAG': "sprite-flag_czech_republic"},
                 'Denmark': {'NAME': {'title': 'Denmark', 'title_ru': 'Дания', "title_en": "Denmark"}, 'COUNTRY_FLAG': "sprite-flag_denmark"},
                 'Djibouti': {'NAME': {'title': 'Djibouti', 'title_ru': 'Джибути', "title_en": "Djibouti"}, 'COUNTRY_FLAG': "sprite-flag_djibouti"},
                 'Dominica': {'NAME': {'title': 'Dominica', 'title_ru': 'Доминика', "title_en": "Dominica"}, 'COUNTRY_FLAG': "sprite-flag_dominica"},
                 'Dominican Republic': {'NAME': {'title': 'Dominican Republic', 'title_ru': 'Доминиканская Республика', "title_en": "Dominican Republic"}, 'COUNTRY_FLAG': "sprite-flag_dominican_republic"},
                 'East Timor': {'NAME': {'title': 'East Timor', 'title_ru': 'Восточный Тимор', "title_en": "East Timor"}, 'COUNTRY_FLAG': "sprite-flag_east_timor"},
                 'Egypt': {'NAME': {'title': 'Egypt', 'title_ru': 'Египет', "title_en": "Egypt"}, 'COUNTRY_FLAG': "sprite-flag_egypt"},
                 'El Salvador': {'NAME': {'title': 'El Salvador', 'title_ru': 'Сальвадор', "title_en": "El Salvador"}, 'COUNTRY_FLAG': "sprite-flag_el_salvador"},
                 'Ecuador': {'NAME': {'title': 'Ecuador', 'title_ru': 'Эквадор', "title_en": "Ecuador"}, 'COUNTRY_FLAG': "sprite-flag_equador"},
                 'Equatorial Guinea': {'NAME': {'title': 'Equatorial Guinea', 'title_ru': 'Экваториальная Гвинея', "title_en": "Equatorial Guinea"}, 'COUNTRY_FLAG': "sprite-flag_equatorial_guinea"},
                 'Eritrea': {'NAME': {'title': 'Eritrea', 'title_ru': 'Эритрея', "title_en": "Eritrea"}, 'COUNTRY_FLAG': "sprite-flag_eritrea"},
                 'Ethiopia': {'NAME': {'title': 'Ethiopia', 'title_ru': 'Эфиопия', "title_en": "Ethiopia"}, 'COUNTRY_FLAG': "sprite-flag_ethiopia"},
                 'Federated State of Micronesia': {'NAME': {'title': 'Federated State of Micronesia', 'title_ru': 'Федеративные Штаты Микронезии', "title_en": "Federated State of Micronesia"}, 'COUNTRY_FLAG': "sprite-flag_federated_states_of_micronesia"},
                 'Fiji': {'NAME': {'title': 'Fiji', 'title_ru': 'Фиджи', "title_en": "Fiji"}, 'COUNTRY_FLAG': "sprite-flag_fiji"},
                 'Finland': {'NAME': {'title': 'Finland', 'title_ru': 'Финляндия', "title_en": "Finland"}, 'COUNTRY_FLAG': "sprite-flag_finland"},
                 'France': {'NAME': {'title': 'France', 'title_ru': 'Франция', "title_en": "France"}, 'COUNTRY_FLAG': "sprite-flag_france"},
                 'Gabon': {'NAME': {'title': 'Gabon', 'title_ru': 'Габон', "title_en": "Gabon"}, 'COUNTRY_FLAG': "sprite-flag_gabon"},
                 'Gambia': {'NAME': {'title': 'Gambia', 'title_ru': 'Гамбия', "title_en": "Gambia"}, 'COUNTRY_FLAG': "sprite-flag_gambia"},
                 'Germany': {'NAME': {'title': 'Germany', 'title_ru': 'Германия', "title_en": "Germany"}, 'COUNTRY_FLAG': "sprite-flag_germany"},
                 'Ghana': {'NAME': {'title': 'Ghana', 'title_ru': 'Гана', "title_en": "Ghana"}, 'COUNTRY_FLAG': "sprite-flag_ghana"},
                 'Greece': {'NAME': {'title': 'Greece', 'title_ru': 'Греция', "title_en": "Greece"}, 'COUNTRY_FLAG': "sprite-flag_greece"},
                 'Grenada': {'NAME': {'title': 'Grenada', 'title_ru': 'Гренада', "title_en": "Grenada"}, 'COUNTRY_FLAG': "sprite-flag_grenada"},
                 'Guatemala': {'NAME': {'title': 'Guatemala', 'title_ru': 'Гватемала', "title_en": "Guatemala"}, 'COUNTRY_FLAG': "sprite-flag_guatemala"},
                 'Guinea': {'NAME': {'title': 'Guinea', 'title_ru': 'Гвинея', "title_en": "Guinea"}, 'COUNTRY_FLAG': "sprite-flag_guinea"},
                 'Guinea Bissau': {'NAME': {'title': 'Guinea Bissau', 'title_ru': 'Гвинея-Бисау', "title_en": "Guinea Bissau"}, 'COUNTRY_FLAG': "sprite-flag_guinea_bissau"},
                 'Guyana': {'NAME': {'title': 'Guyana', 'title_ru': 'Гайана', "title_en": "Guyana"}, 'COUNTRY_FLAG': "sprite-flag_guyana"},
                 'Haiti': {'NAME': {'title': 'Haiti', 'title_ru': 'Гаити', "title_en": "Haiti"}, 'COUNTRY_FLAG': "sprite-flag_haiti"},
                 'Honduras': {'NAME': {'title': 'Honduras', 'title_ru': 'Гондурас', "title_en": "Honduras"}, 'COUNTRY_FLAG': "sprite-flag_honduras"},
                 'Hungary': {'NAME': {'title': 'Hungary', 'title_ru': 'Венгрия', "title_en": "Hungary"}, 'COUNTRY_FLAG': "sprite-flag_hungary"},
                 'Iceland': {'NAME': {'title': 'Iceland', 'title_ru': 'Исландия', "title_en": "Iceland"}, 'COUNTRY_FLAG': "sprite-flag_iceland"},
                 'India': {'NAME': {'title': 'India', 'title_ru': 'Индия', "title_en": "India"}, 'COUNTRY_FLAG': "sprite-flag_india"},
                 'Indonesia': {'NAME': {'title': 'Indonesia', 'title_ru': 'Индонезия', "title_en": "Indonesia"}, 'COUNTRY_FLAG': "sprite-flag_indonesia"},
                 'Iran': {'NAME': {'title': 'Iran', 'title_ru': 'Иран', "title_en": "Iran"}, 'COUNTRY_FLAG': "sprite-flag_iran"},
                 'Iraq': {'NAME': {'title': 'Iraq', 'title_ru': 'Ирак', "title_en": "Iraq"}, 'COUNTRY_FLAG': "sprite-flag_iraq"},
                 'Ireland': {'NAME': {'title': 'Ireland', 'title_ru': 'Ирландия', "title_en": "Ireland"}, 'COUNTRY_FLAG': "sprite-flag_ireland"},
                 'Italy': {'NAME': {'title': 'Italy', 'title_ru': 'Италия', "title_en": "Italy"}, 'COUNTRY_FLAG': "sprite-flag_italy"},
                 'Jamaica': {'NAME': {'title': 'Jamaica', 'title_ru': 'Ямайка', "title_en": "Jamaica"}, 'COUNTRY_FLAG': "sprite-flag_jamaica"},
                 'Japan': {'NAME': {'title': 'Japan', 'title_ru': 'Япония', "title_en": "Japan"}, 'COUNTRY_FLAG': "sprite-flag_japan"},
                 'Jordan': {'NAME': {'title': 'Jordan', 'title_ru': 'Иордания', "title_en": "Jordan"}, 'COUNTRY_FLAG': "sprite-flag_jordan"},
                 'Kenya': {'NAME': {'title': 'Kenya', 'title_ru': 'Кения', "title_en": "Kenya"}, 'COUNTRY_FLAG': "sprite-flag_kenya"},
                 'Kiribati': {'NAME': {'title': 'Kiribati', 'title_ru': 'Кирибати', "title_en": "Kiribati"}, 'COUNTRY_FLAG': "sprite-flag_kiribati"},
                 'Kuwait': {'NAME': {'title': 'Kuwait', 'title_ru': 'Кувейт', "title_en": "Kuwait"}, 'COUNTRY_FLAG': "sprite-flag_kuwait"},
                 'Laos': {'NAME': {'title': 'Laos', 'title_ru': 'Лаос', "title_en": "Laos"}, 'COUNTRY_FLAG': "sprite-flag_laos"},
                 'Lebanon': {'NAME': {'title': 'Lebanon', 'title_ru': 'Ливан', "title_en": "Lebanon"}, 'COUNTRY_FLAG': "sprite-flag_lebanon"},
                 'Lesotho': {'NAME': {'title': 'Lesotho', 'title_ru': 'Лесото', "title_en": "Lesotho"}, 'COUNTRY_FLAG': "sprite-flag_lesotho"},
                 'Liberia': {'NAME': {'title': 'Liberia', 'title_ru': 'Либерия', "title_en": "Liberia"}, 'COUNTRY_FLAG': "sprite-flag_liberia"},
                 'Libya': {'NAME': {'title': 'Libya', 'title_ru': 'Ливия', "title_en": "Libya"}, 'COUNTRY_FLAG': "sprite-flag_libya"},
                 'Liechtenstein': {'NAME': {'title': 'Liechtenstein', 'title_ru': 'Лихтенштейн', "title_en": "Liechtenstein"}, 'COUNTRY_FLAG': "sprite-flag_liechtenstein"},
                 'Luxembourg': {'NAME': {'title': 'Luxembourg', 'title_ru': 'Люксембург', "title_en": "Luxembourg"}, 'COUNTRY_FLAG': "sprite-flag_luxembourg"},
                 'Macedonia': {'NAME': {'title': 'Macedonia', 'title_ru': 'Македония', "title_en": "Macedonia"}, 'COUNTRY_FLAG': "sprite-flag_macedonia"},
                 'Madagascar': {'NAME': {'title': 'Madagascar', 'title_ru': 'Мадагаскар', "title_en": "Madagascar"}, 'COUNTRY_FLAG': "sprite-flag_madagascar"},
                 'Malawi': {'NAME': {'title': 'Malawi', 'title_ru': 'Малави', "title_en": "Malawi"}, 'COUNTRY_FLAG': "sprite-flag_malawi"},
                 'Malaysia': {'NAME': {'title': 'Malaysia', 'title_ru': 'Малайзия', "title_en": "Malaysia"}, 'COUNTRY_FLAG': "sprite-flag_malaysia"},
                 'Maldives': {'NAME': {'title': 'Maldives', 'title_ru': 'Мальдивы', "title_en": "Maldives"}, 'COUNTRY_FLAG': "sprite-flag_maledives"},
                 'Mali': {'NAME': {'title': 'Mali', 'title_ru': 'Мали', "title_en": "Mali"}, 'COUNTRY_FLAG': "sprite-flag_mali"},
                 'Malta': {'NAME': {'title': 'Malta', 'title_ru': 'Мальта', "title_en": "Malta"}, 'COUNTRY_FLAG': "sprite-flag_malta"},
                 'Marshall Islands': {'NAME': {'title': 'Marshall Islands', 'title_ru': 'Маршалловы острова', "title_en": "Marshall Islands"}, 'COUNTRY_FLAG': "sprite-flag_marshall_islands"},
                 'Mauretania': {'NAME': {'title': 'Mauretania', 'title_ru': 'Мавритания', "title_en": "Mauretania"}, 'COUNTRY_FLAG': "sprite-flag_mauretania"},
                 'Mauritius': {'NAME': {'title': 'Mauritius', 'title_ru': 'Маврикий', "title_en": "Mauritius"}, 'COUNTRY_FLAG': "sprite-flag_mauritius"},
                 'Mexico': {'NAME': {'title': 'Mexico', 'title_ru': 'Мексика', "title_en": "Mexico"}, 'COUNTRY_FLAG': "sprite-flag_mexico"},
                 'Monaco': {'NAME': {'title': 'Monaco', 'title_ru': 'Монако', "title_en": "Monaco"}, 'COUNTRY_FLAG': "sprite-flag_monaco"},
                 'Mongolia': {'NAME': {'title': 'Mongolia', 'title_ru': 'Монголия', "title_en": "Mongolia"}, 'COUNTRY_FLAG': "sprite-flag_mongolia"},
                 'Montenegro': {'NAME': {'title': 'Montenegro', 'title_ru': 'Черногория', "title_en": "Montenegro"}, 'COUNTRY_FLAG': "sprite-flag_montenegro"},
                 'Morocco': {'NAME': {'title': 'Morocco', 'title_ru': 'Марокко', "title_en": "Morocco"}, 'COUNTRY_FLAG': "sprite-flag_morocco"},
                 'Mozambique': {'NAME': {'title': 'Mozambique', 'title_ru': 'Мозамбик', "title_en": "Mozambique"}, 'COUNTRY_FLAG': "sprite-flag_mozambique"},
                 'Myanmar': {'NAME': {'title': 'Myanmar', 'title_ru': 'Мьянма', "title_en": "Myanmar"}, 'COUNTRY_FLAG': "sprite-flag_myanmar"},
                 'Namibia': {'NAME': {'title': 'Namibia', 'title_ru': 'Намибия', "title_en": "Namibia"}, 'COUNTRY_FLAG': "sprite-flag_namibia"},
                 'Nauru': {'NAME': {'title': 'Nauru', 'title_ru': 'Науру', "title_en": "Nauru"}, 'COUNTRY_FLAG': "sprite-flag_nauru"},
                 'Nepal': {'NAME': {'title': 'Nepal', 'title_ru': 'Непал', "title_en": "Nepal"}, 'COUNTRY_FLAG': "sprite-flag_nepal"},
                 'Netherlands': {'NAME': {'title': 'Netherlands', 'title_ru': 'Нидерланды', "title_en": "Netherlands"}, 'COUNTRY_FLAG': "sprite-flag_netherlands"},
                 'New Zealand': {'NAME': {'title': 'New Zealand', 'title_ru': 'Новая Зеландия', "title_en": "New Zealand"}, 'COUNTRY_FLAG': "sprite-flag_new_zealand"},
                 'Nicaragua': {'NAME': {'title': 'Nicaragua', 'title_ru': 'Никарагуа', "title_en": "Nicaragua"}, 'COUNTRY_FLAG': "sprite-flag_nicaragua"},
                 'Niger': {'NAME': {'title': 'Niger', 'title_ru': 'Нигер', "title_en": "Niger"}, 'COUNTRY_FLAG': "sprite-flag_niger"},
                 'Nigeria': {'NAME': {'title': 'Nigeria', 'title_ru': 'Нигерия', "title_en": "Nigeria"}, 'COUNTRY_FLAG': "sprite-flag_nigeria"},
                 'Niue': {'NAME': {'title': 'Niue', 'title_ru': 'Ниуэ', "title_en": "Niue"}, 'COUNTRY_FLAG': "sprite-flag_niue"},
                 'North Korea': {'NAME': {'title': 'North Korea', 'title_ru': 'Северная Корея', "title_en": "North Korea"}, 'COUNTRY_FLAG': "sprite-flag_north_korea"},
                 'Norway': {'NAME': {'title': 'Norway', 'title_ru': 'Норвегия', "title_en": "Norway"}, 'COUNTRY_FLAG': "sprite-flag_norway"},
                 'Oman': {'NAME': {'title': 'Oman', 'title_ru': 'Оман', "title_en": "Oman"}, 'COUNTRY_FLAG': "sprite-flag_oman"},
                 'Pakistan': {'NAME': {'title': 'Pakistan', 'title_ru': 'Пакистан', "title_en": "Pakistan"}, 'COUNTRY_FLAG': "sprite-flag_pakistan"},
                 'Palau': {'NAME': {'title': 'Palau', 'title_ru': 'Палау', "title_en": "Palau"}, 'COUNTRY_FLAG': "sprite-flag_palau"},
                 'Palestine': {'NAME': {'title': 'Palestine', 'title_ru': 'Палестина', "title_en": "Palestine"}, 'COUNTRY_FLAG': "sprite-flag_palestine"},
                 'Panama': {'NAME': {'title': 'Panama', 'title_ru': 'Панама', "title_en": "Panama"}, 'COUNTRY_FLAG': "sprite-flag_panama"},
                 'Papua New Guinea': {'NAME': {'title': 'Papua New Guinea', 'title_ru': 'Папуа-Новая Гвинея', "title_en": "Papua New Guinea"}, 'COUNTRY_FLAG': "sprite-flag_papua_new_guinea"},
                 'Paraguay': {'NAME': {'title': 'Paraguay', 'title_ru': 'Парагвай', "title_en": "Paraguay"}, 'COUNTRY_FLAG': "sprite-flag_paraquay"},
                 'Peru': {'NAME': {'title': 'Peru', 'title_ru': 'Перу', "title_en": "Peru"}, 'COUNTRY_FLAG': "sprite-flag_peru"},
                 'Philippines': {'NAME': {'title': 'Philippines', 'title_ru': 'Филиппины', "title_en": "Philippines"}, 'COUNTRY_FLAG': "sprite-flag_philippines"},
                 'Poland': {'NAME': {'title': 'Poland', 'title_ru': 'Польша', "title_en": "Poland"}, 'COUNTRY_FLAG': "sprite-flag_poland"},
                 'Portugal': {'NAME': {'title': 'Portugal', 'title_ru': 'Португалия', "title_en": "Portugal"}, 'COUNTRY_FLAG': "sprite-flag_portugal"},
                 'Qatar': {'NAME': {'title': 'Qatar', 'title_ru': 'Катар', "title_en": "Qatar"}, 'COUNTRY_FLAG': "sprite-flag_qatar"},
                 'Romania': {'NAME': {'title': 'Romania', 'title_ru': 'Румыния', "title_en": "Romania"}, 'COUNTRY_FLAG': "sprite-flag_romania"},
                 'Rwanda': {'NAME': {'title': 'Rwanda', 'title_ru': 'Руанда', "title_en": "Rwanda"}, 'COUNTRY_FLAG': "sprite-flag_rwanda"},
                 'Saint Kitts and Nevis': {'NAME': {'title': 'Saint Kitts and Nevis', 'title_ru': 'Сент-Китс и Невис', "title_en": "Saint Kitts and Nevis"}, 'COUNTRY_FLAG': "sprite-flag_saint_kitts_and_nevis"},
                 'Saint Lucia': {'NAME': {'title': 'Saint Lucia', 'title_ru': 'Сент-Люсия', "title_en": "Saint Lucia"}, 'COUNTRY_FLAG': "sprite-flag_saint_lucia"},
                 'Saint Vincent and the Grenadines': {'NAME': {'title': 'Saint Vincent and the Grenadines', 'title_ru': 'Сент-Винсент и Гренадины', "title_en": "Saint Vincent and the Grenadines"}, 'COUNTRY_FLAG': "sprite-flag_saint_vincent_and_the_grenadines"},
                 'Samoa': {'NAME': {'title': 'Samoa', 'title_ru': 'Самоа', "title_en": "Samoa"}, 'COUNTRY_FLAG': "sprite-flag_samoa"},
                 'San Marino': {'NAME': {'title': 'San Marino', 'title_ru': 'Сан - Марино', "title_en": "San Marino"}, 'COUNTRY_FLAG': "sprite-flag_san_marino"},
                 'Sao Tome and Principe': {'NAME': {'title': 'Sao Tome and Principe', 'title_ru': 'Сан-Томе и Принсипи', "title_en": "Sao Tome and Principe"}, 'COUNTRY_FLAG': "sprite-flag_sao_tome_and_principe"},
                 'Saudi Arabia': {'NAME': {'title': 'Saudi Arabia', 'title_ru': 'Саудовская Аравия', "title_en": "Saudi Arabia"}, 'COUNTRY_FLAG': "sprite-flag_saudi_arabia"},
                 'Senegal': {'NAME': {'title': 'Senegal', 'title_ru': 'Сенегал', "title_en": "Senegal"}, 'COUNTRY_FLAG': "sprite-flag_senegal"},
                 'Serbia': {'NAME': {'title': 'Serbia', 'title_ru': 'Сербия', "title_en": "Serbia"}, 'COUNTRY_FLAG': "sprite-flag_serbia"},
                 'Seychelles': {'NAME': {'title': 'Seychelles', 'title_ru': 'Сейшельские острова', "title_en": "Seychelles"}, 'COUNTRY_FLAG': "sprite-flag_seychelles"},
                 'Sierra Leone': {'NAME': {'title': 'Sierra Leone', 'title_ru': 'Сьерра-Леоне', "title_en": "Sierra Leone"}, 'COUNTRY_FLAG': "sprite-flag_sierra_leone"},
                 'Singapore': {'NAME': {'title': 'Singapore', 'title_ru': 'Сингапур', "title_en": "Singapore"}, 'COUNTRY_FLAG': "sprite-flag_singapore"},
                 'Slovakia': {'NAME': {'title': 'Slovakia', 'title_ru': 'Словакия', "title_en": "Slovakia"}, 'COUNTRY_FLAG': "sprite-flag_slovakia"},
                 'Slovenia': {'NAME': {'title': 'Slovenia', 'title_ru': 'Словения', "title_en": "Slovenia"}, 'COUNTRY_FLAG': "sprite-flag_slovenia"},
                 'Solomon Islands': {'NAME': {'title': 'Solomon Islands', 'title_ru': 'Соломоновы Острова', "title_en": "Solomon Islands"}, 'COUNTRY_FLAG': "sprite-flag_solomon_islands"},
                 'Somalia': {'NAME': {'title': 'Somalia', 'title_ru': 'Сомали', "title_en": "Somalia"}, 'COUNTRY_FLAG': "sprite-flag_somalia"},
                 'South Africa': {'NAME': {'title': 'South Africa', 'title_ru': 'ЮАР', "title_en": "South Africa"}, 'COUNTRY_FLAG': "sprite-flag_south_africa"},
                 'South Korea': {'NAME': {'title': 'South Korea', 'title_ru': 'Южная Корея', "title_en": "South Korea"}, 'COUNTRY_FLAG': "sprite-flag_south_korea"},
                 'South Sudan': {'NAME': {'title': 'South Sudan', 'title_ru': 'Южный Судан', "title_en": "South Sudan"}, 'COUNTRY_FLAG': "sprite-flag_south_sudan"},
                 'Spain': {'NAME': {'title': 'Spain', 'title_ru': 'Испания', "title_en": "Spain"}, 'COUNTRY_FLAG': "sprite-flag_spain"},
                 'Sri Lanka': {'NAME': {'title': 'Sri Lanka', 'title_ru': 'Шри Ланка', "title_en": "Sri Lanka"}, 'COUNTRY_FLAG': "sprite-flag_sri_lanka"},
                 'Sudan': {'NAME': {'title': 'Sudan', 'title_ru': 'Судан', "title_en": "Sudan"}, 'COUNTRY_FLAG': "sprite-flag_sudan"},
                 'Suriname': {'NAME': {'title': 'Suriname', 'title_ru': 'Суринам', "title_en": "Suriname"}, 'COUNTRY_FLAG': "sprite-flag_suriname"},
                 'Swaziland': {'NAME': {'title': 'Swaziland', 'title_ru': 'Свазиленд', "title_en": "Swaziland"}, 'COUNTRY_FLAG': "sprite-flag_swaziland"},
                 'Sweden': {'NAME': {'title': 'Sweden', 'title_ru': 'Швеция', "title_en": "Sweden"}, 'COUNTRY_FLAG': "sprite-flag_sweden"},
                 'Switzerland': {'NAME': {'title': 'Switzerland', 'title_ru': 'Швейцария', "title_en": "Switzerland"}, 'COUNTRY_FLAG': "sprite-flag_switzerland"},
                 'Syria': {'NAME': {'title': 'Syria', 'title_ru': 'Сирия', "title_en": "Syria"}, 'COUNTRY_FLAG': "sprite-flag_syria"},
                 'Tanzania': {'NAME': {'title': 'Tanzania', 'title_ru': 'Танзания', "title_en": "Tanzania"}, 'COUNTRY_FLAG': "sprite-flag_tanzania"},
                 'Thailand': {'NAME': {'title': 'Thailand', 'title_ru': 'Таиланд', "title_en": "Thailand"}, 'COUNTRY_FLAG': "sprite-flag_thailand"},
                 'Togo': {'NAME': {'title': 'Togo', 'title_ru': 'Того', "title_en": "Togo"}, 'COUNTRY_FLAG': "sprite-flag_togo"},
                 'Tonga': {'NAME': {'title': 'Tonga', 'title_ru': 'Тонга', "title_en": "Tonga"}, 'COUNTRY_FLAG': "sprite-flag_tonga"},
                 'Trinidad and Tobago': {'NAME': {'title': 'Trinidad and Tobago', 'title_ru': 'Тринидад и Тобаго', "title_en": "Trinidad and Tobago"}, 'COUNTRY_FLAG': "sprite-flag_trinidad_and_tobago"},
                 'Tunisia': {'NAME': {'title': 'Tunisia', 'title_ru': 'Тунис', "title_en": "Tunisia"}, 'COUNTRY_FLAG': "sprite-flag_tunisia"},
                 'Turkey': {'NAME': {'title': 'Turkey', 'title_ru': 'Турция', "title_en": "Turkey"}, 'COUNTRY_FLAG': "sprite-flag_turkey"},
                 'Tuvalu': {'NAME': {'title': 'Tuvalu', 'title_ru': 'Тувалу', "title_en": "Tuvalu"}, 'COUNTRY_FLAG': "sprite-flag_tuvalu"},
                 'Uganda': {'NAME': {'title': 'Uganda', 'title_ru': 'Уганда', "title_en": "Uganda"}, 'COUNTRY_FLAG': "sprite-flag_uganda"},
                 'United Arab Emirates': {'NAME': {'title': 'United Arab Emirates', 'title_ru': 'Объединенные Арабские Эмираты', "title_en": "United Arab Emirates"}, 'COUNTRY_FLAG': "sprite-flag_united_arab_emirates"},
                 'United Kingdom': {'NAME': {'title': 'United Kingdom', 'title_ru': 'Великобритания', "title_en": "United Kingdom"}, 'COUNTRY_FLAG': "sprite-flag_united_kingdom"},
                 'Uruguay': {'NAME': {'title': 'Uruguay', 'title_ru': 'Уругвай', "title_en": "Uruguay"}, 'COUNTRY_FLAG': "sprite-flag_uruquay"},
                 'USA': {'NAME': {'title': 'USA', 'title_ru': 'США', "title_en": "USA"}, 'COUNTRY_FLAG': "sprite-flag_usa"},
                 'Vanuatu': {'NAME': {'title': 'Vanuatu', 'title_ru': 'Вануату', "title_en": "Vanuatu"}, 'COUNTRY_FLAG': "sprite-flag_vanuatu"},
                 'Vatican City': {'NAME': {'title': 'Vatican City', 'title_ru': 'Ватикан', "title_en": "Vatican City"}, 'COUNTRY_FLAG': "sprite-flag_vatican_city"},
                 'Venezuela': {'NAME': {'title': 'Venezuela', 'title_ru': 'Венесуэла', "title_en": "Venezuela"}, 'COUNTRY_FLAG': "sprite-flag_venezuela"},
                 'Vietnam': {'NAME': {'title': 'Vietnam', 'title_ru': 'Вьетнам', "title_en": "Vietnam"}, 'COUNTRY_FLAG': "sprite-flag_vietnam"},
                 'Yemen': {'NAME': {'title': 'Yemen', 'title_ru': 'Йемен', "title_en": "Yemen"}, 'COUNTRY_FLAG': "sprite-flag_yemen"},
                 'Zambia': {'NAME': {'title': 'Zambia', 'title_ru': 'Замбия', "title_en": "Zambia"}, 'COUNTRY_FLAG': "sprite-flag_zambia"},
                 'Zimbabwe': {'NAME': {'title': 'Zimbabwe', 'title_ru': 'Зимбабве', "title_en": "Zimbabwe"}, 'COUNTRY_FLAG': "sprite-flag_zimbabwe"},

    }

    for title, attr in countries.items():
        cntr, res = Country.objects.get_or_create(title=title, create_user=crt_usr)
        cntr.setAttributeValue({'NAME': attr['NAME']['title_en']}, crt_usr)
        cntr.setAttributeValue({'COUNTRY_FLAG': attr['COUNTRY_FLAG']}, crt_usr)


    return HttpResponse('Successfully')
      

def builTemplate(request):
    if request.user.is_superuser:
        crt_usr = User.objects.get(pk=request.user.pk)
        templates = {'tourism': {'NAME': {'title': 'Tourism', 'title_ru': 'Туризм'}, 'TEMPLATE_IMAGE_FOLDER': "tourism"} ,
                     'advocacy': {'NAME': {'title': 'Advocacy', 'title_ru': 'Адвокатура'}, 'TEMPLATE_IMAGE_FOLDER': "advocacy"},
                     'agriculture': {'NAME': {'title': 'Agriculture', 'title_ru': 'Сельское хозяйство'}, 'TEMPLATE_IMAGE_FOLDER': "agriculture"},
                     'architecture': {'NAME': {'title': 'Architecture and Engineering jobs', 'title_ru': 'Архитектура и Инженерные работы'}, 'TEMPLATE_IMAGE_FOLDER': "architecture"},
                     'art': {'NAME': {'title': 'Art and Photography', 'title_ru': 'Искусство и Фото'}, 'TEMPLATE_IMAGE_FOLDER': "art"},
                     'auditors': {'NAME': {'title': 'Auditors', 'title_ru': 'Аудиторы'}, 'TEMPLATE_IMAGE_FOLDER': "auditors"},
                     'brokerage': {'NAME': {'title': 'Brokerage', 'title_ru': 'Брокерские компании'}, 'TEMPLATE_IMAGE_FOLDER': "brokerage"},
                     'communications': {'NAME': {'title': 'Communications and Electronics', 'title_ru': 'Связь и электроника'}, 'TEMPLATE_IMAGE_FOLDER': "communications"},
                     'comuters': {'NAME': {'title': 'Computers and IT', 'title_ru': 'Компьютеры и IT'}, 'TEMPLATE_IMAGE_FOLDER': "comuters"},
                     'consumer_services': {'NAME': {'title': 'Domestic services', 'title_ru': 'Бытовые услуги'}, 'TEMPLATE_IMAGE_FOLDER': "consumer_services"},
                     'culture': {'NAME': {'title': 'Culture and Society', 'title_ru': 'Культура и Общество'}, 'TEMPLATE_IMAGE_FOLDER': "culture"},
                     'entertainment': {'NAME': {'title': 'Entertainment, Food and Drink', 'title_ru': 'Развлечения, Еда и Напитки'}, 'TEMPLATE_IMAGE_FOLDER': "entertainment"},
                     'fasion': {'NAME': {'title': 'Fasion', 'title_ru': 'Мода'}, 'TEMPLATE_IMAGE_FOLDER': "fasion"},
                     'fiance': {'NAME': {'title': 'Business and Finance', 'title_ru': 'Бизнес и финансы'}, 'TEMPLATE_IMAGE_FOLDER': "fiance"},
                     'furniture': {'NAME': {'title': 'Furniture and Interior', 'title_ru': 'Мебель и Интерьер'}, 'TEMPLATE_IMAGE_FOLDER': "furniture"},
                     'import_export': {'NAME': {'title': 'Import and Export', 'title_ru': 'Импорт и экспорт'}, 'TEMPLATE_IMAGE_FOLDER': "import_export"},
                     'industrial': {'NAME': {'title': 'Industrial and Equipment', 'title_ru': 'Промышленность и оборудование'}, 'TEMPLATE_IMAGE_FOLDER': "industrial"},
                     'insurance': {'NAME': {'title': 'Insurance', 'title_ru': 'Страхование'}, 'TEMPLATE_IMAGE_FOLDER': "insurance"},
                     'jewelry': {'NAME': {'title': 'Jewelry', 'title_ru': 'Роскошь и украшения'}, 'TEMPLATE_IMAGE_FOLDER': "jewelry"},
                     'medicine': {'NAME': {'title': 'Medicine', 'title_ru': 'Медицина и здоровье'}, 'TEMPLATE_IMAGE_FOLDER': "medicine"},
                     'real_estate': {'NAME': {'title': 'Real estate', 'title_ru': 'Недвижимость'}, 'TEMPLATE_IMAGE_FOLDER': "real_estate"},
                     'science': {'NAME': {'title': 'Science and Education', 'title_ru': 'Наука и Образование'}, 'TEMPLATE_IMAGE_FOLDER': "science"},
                     'security': {'NAME': {'title': 'Security', 'title_ru': 'Безопасность'}, 'TEMPLATE_IMAGE_FOLDER': "security"},
                     'transport': {'NAME': {'title': 'Transport', 'title_ru': 'Транспорт - АвтоМото'}, 'TEMPLATE_IMAGE_FOLDER': "transport"},

                     }


        for title, attr in templates.items():
            cntr, res = ExternalSiteTemplate.objects.get_or_create(title=title, create_user=crt_usr)
            if res:
                cntr.setAttributeValue({'NAME': attr['NAME']}, crt_usr)
                cntr.setAttributeValue({'TEMPLATE_IMAGE_FOLDER': attr['TEMPLATE_IMAGE_FOLDER']}, crt_usr)