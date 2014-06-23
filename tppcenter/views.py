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
    countries = {'Azerbaydjan': {'NAME': {'title_en': 'Azerbaydjan', 'title_ru': 'Азербайджан'}, 'COUNTRY_FLAG': "sprite-flag_azerbaijan"},
                 'Armenia': {'NAME': {'title_en': 'Armenia', 'title_ru': 'Армения'}, 'COUNTRY_FLAG': "sprite-flag_armenia"},
                 'Belarus': {'NAME': {'title_en': 'Belarus', 'title_ru': 'Беларусь'}, 'COUNTRY_FLAG': "sprite-flag_belarus"},
                 'Georgia': {'NAME': {'title_en': 'Georgia', 'title_ru': 'Грузия'}, 'COUNTRY_FLAG': "sprite-flag_georgia"},
                 'Israel': {'NAME': {'title_en': 'Israel', 'title_ru': 'Израиль'}, 'COUNTRY_FLAG': "sprite-flag_israel"},
                 'Kazakhstan': {'NAME': {'title_en': 'Kazakhstan', 'title_ru': 'Казахстан'}, 'COUNTRY_FLAG': "sprite-flag_kazakhstan"},
                 'Kyrgyzstan': {'NAME': {'title_en': 'Kyrgyzstan', 'title_ru': 'Киргизия'}, 'COUNTRY_FLAG': "sprite-flag_kyrgyzstan"},
                 'Latvia': {'NAME': {'title_en': 'Latvia', 'title_ru': 'Латвия'}, 'COUNTRY_FLAG': "sprite-flag_lithuania"},
                 'Lithuania': {'NAME': {'title_en': 'Lithuania', 'title_ru': 'Литва'}, 'COUNTRY_FLAG': "sprite-flag_lithuania"},
                 'Moldova': {'NAME': {'title_en': 'Moldova', 'title_ru': 'Молдова'}, 'COUNTRY_FLAG': "sprite-flag_moldova"},
                 'Russia': {'NAME': {'title_en': 'Russia', 'title_ru': 'Россия'}, 'COUNTRY_FLAG': "sprite-flag_russia"},
                 'Tajikistan': {'NAME': {'title_en': 'Tajikistan', 'title_ru': 'Таджикистан'}, 'COUNTRY_FLAG': "sprite-flag_tajikistan"},
                 'Turkmenistan': {'NAME': {'title_en': 'Turkmenistan', 'title_ru': 'Туркмения'}, 'COUNTRY_FLAG': "sprite-flag_turkmenistan"},
                 'Uzbekistan': {'NAME': {'title_en': 'Uzbekistan', 'title_ru': 'Узбекистан'}, 'COUNTRY_FLAG': "sprite-flag_uzbekistan"},
                 'Ukraine': {'NAME': {'title_en': 'Ukraine', 'title_ru': 'Украина'}, 'COUNTRY_FLAG': "sprite-flag_ukraine"},
                 'Estonia': {'NAME': {'title_en': 'Estonia', 'title_ru': 'Эстония'}, 'COUNTRY_FLAG': "sprite-flag_estonia"},
                 'Afghanistan': {'NAME': {'title_en': 'Afghanistan', 'title_ru': 'Афганистан'}, 'COUNTRY_FLAG': "sprite-flag_afghanistan"},
                 'Albania': {'NAME': {'title_en': 'Albania', 'title_ru': 'Албания'}, 'COUNTRY_FLAG': "sprite-flag_albania"},
                 'Algeria': {'NAME': {'title_en': 'Algeria', 'title_ru': 'Алжир'}, 'COUNTRY_FLAG': "sprite-flag_algeria"},
                 'Andorra': {'NAME': {'title_en': 'Andorra', 'title_ru': 'Андорра'}, 'COUNTRY_FLAG': "sprite-flag_andorra"},
                 'Angola': {'NAME': {'title_en': 'Angola', 'title_ru': 'Ангола'}, 'COUNTRY_FLAG': "sprite-flag_angola"},
                 'Antigua and Barbuda': {'NAME': {'title_en': 'Antigua and Barbuda', 'title_ru': 'Антигуа и Барбуда'}, 'COUNTRY_FLAG': "sprite-flag_antigua_and_barbuda"},
                 'Argentina': {'NAME': {'title_en': 'Argentina', 'title_ru': 'Аргентина'}, 'COUNTRY_FLAG': "sprite-flag_argentina"},
                 'Australia': {'NAME': {'title_en': 'Australia', 'title_ru': 'Австралия'}, 'COUNTRY_FLAG': "sprite-flag_australia"},
                 'Austria': {'NAME': {'title_en': 'Austria', 'title_ru': 'Австрия'}, 'COUNTRY_FLAG': "sprite-flag_austria"},
                 'Bahamas': {'NAME': {'title_en': 'Bahamas', 'title_ru': 'Багамские острова'}, 'COUNTRY_FLAG': "sprite-flag_bahamas"},
                 'Bahrain': {'NAME': {'title_en': 'Bahrain', 'title_ru': 'Бахрейн'}, 'COUNTRY_FLAG': "sprite-flag_bahrain"},
                 'Bangladesh': {'NAME': {'title_en': 'Bangladesh', 'title_ru': 'Бангладеш'}, 'COUNTRY_FLAG': "sprite-flag_bangladesh"},
                 'Barbados': {'NAME': {'title_en': 'Barbados', 'title_ru': 'Барбадос'}, 'COUNTRY_FLAG': "sprite-flag_barbados"},
                 'Belgium': {'NAME': {'title_en': 'Belgium', 'title_ru': 'Бельгия'}, 'COUNTRY_FLAG': "sprite-flag_belgium"},
                 'Belize': {'NAME': {'title_en': 'Belize', 'title_ru': 'Белиз'}, 'COUNTRY_FLAG': "sprite-flag_belize"},
                 'Benin': {'NAME': {'title_en': 'Benin', 'title_ru': 'Бенин'}, 'COUNTRY_FLAG': "sprite-flag_benin"},
                 'Bhutan': {'NAME': {'title_en': 'Bhutan', 'title_ru': 'Бутан'}, 'COUNTRY_FLAG': "sprite-flag_bhutan"},
                 'Bolivia': {'NAME': {'title_en': 'Bolivia', 'title_ru': 'Боливия'}, 'COUNTRY_FLAG': "sprite-flag_bolivia"},
                 'Bosnia and Herzegovina': {'NAME': {'title_en': 'Bosnia and Herzegovina', 'title_ru': 'Босния и Герцеговина'}, 'COUNTRY_FLAG': "sprite-flag_bosnia_and_herzegovina"},
                 'Botswana': {'NAME': {'title_en': 'Botswana', 'title_ru': 'Ботсвана'}, 'COUNTRY_FLAG': "sprite-flag_botswana"},
                 'Brazil': {'NAME': {'title_en': 'Brazil', 'title_ru': 'Бразилия'}, 'COUNTRY_FLAG': "sprite-flag_brazil"},
                 'Brunei': {'NAME': {'title_en': 'Brunei', 'title_ru': 'Бруней'}, 'COUNTRY_FLAG': "sprite-flag_brunei"},
                 'Bulgaria': {'NAME': {'title_en': 'Bulgaria', 'title_ru': 'Болгария'}, 'COUNTRY_FLAG': "sprite-flag_bulgaria"},
                 'Burkina Faso': {'NAME': {'title_en': 'Burkina Faso', 'title_ru': 'Буркина-Фасо'}, 'COUNTRY_FLAG': "sprite-flag_burkina_faso"},
                 'Burundi': {'NAME': {'title_en': 'Burundi', 'title_ru': 'Бурунди'}, 'COUNTRY_FLAG': "sprite-flag_burundi"},
                 'Cambodia': {'NAME': {'title_en': 'Cambodia', 'title_ru': 'Камбоджа'}, 'COUNTRY_FLAG': "sprite-flag_cambodia"},
                 'Cameroon': {'NAME': {'title_en': 'Cameroon', 'title_ru': 'Камерун'}, 'COUNTRY_FLAG': "sprite-flag_cameroon"},
                 'Canada': {'NAME': {'title_en': 'Canada', 'title_ru': 'Канада'}, 'COUNTRY_FLAG': "sprite-flag_canada"},
                 'Cape Verde': {'NAME': {'title_en': 'Cape Verde', 'title_ru': 'Кабо-Верде'}, 'COUNTRY_FLAG': "sprite-flag_cape_verde"},
                 'Central African Republic': {'NAME': {'title_en': 'Central African Republic', 'title_ru': 'Центрально-Африканская Республика'}, 'COUNTRY_FLAG': "sprite-flag_central_african_republic"},
                 'Chad': {'NAME': {'title_en': 'Chad', 'title_ru': 'Чад'}, 'COUNTRY_FLAG': "sprite-flag_chad"},
                 'Chile': {'NAME': {'title_en': 'Chile', 'title_ru': 'Чили'}, 'COUNTRY_FLAG': "sprite-flag_chile"},
                 'China': {'NAME': {'title_en': 'China', 'title_ru': 'Китай'}, 'COUNTRY_FLAG': "sprite-flag_china"},
                 'Columbia': {'NAME': {'title_en': 'Columbia', 'title_ru': 'Колумбия'}, 'COUNTRY_FLAG': "sprite-flag_colombia"},
                 'Comoros': {'NAME': {'title_en': 'Comoros', 'title_ru': 'Коморские острова'}, 'COUNTRY_FLAG': "sprite-flag_comoros"},
                 'Democratic Republic of Congo': {'NAME': {'title_en': 'Democratic Republic of Congo', 'title_ru': 'Демократическая Республика Конго'}, 'COUNTRY_FLAG': "sprite-flag_congo_democratic_republic"},
                 'Congo Republic': {'NAME': {'title_en': 'Congo Republic', 'title_ru': 'Республика Конго'}, 'COUNTRY_FLAG': "sprite-flag_congo_republic"},
                 'Cook Island': {'NAME': {'title_en': 'Cook Island', 'title_ru': 'острова Кука'}, 'COUNTRY_FLAG': "sprite-flag_cook_islands"},
                 'Costa Rica': {'NAME': {'title_en': 'Costa Rica', 'title_ru': 'Коста-Рика'}, 'COUNTRY_FLAG': "sprite-flag_costa_rica"},
                 "Cote D'ivoire": {'NAME': {'title_en': "Cote D'ivoire", 'title_ru': 'Берег Слоновой Кости'}, 'COUNTRY_FLAG': "sprite-flag_cote_divoire"},
                 'Croatia': {'NAME': {'title_en': 'Croatia', 'title_ru': 'Хорватия'}, 'COUNTRY_FLAG': "sprite-flag_croatia"},
                 'Cuba': {'NAME': {'title_en': 'Cuba', 'title_ru': 'Куба'}, 'COUNTRY_FLAG': "sprite-flag_cuba"},
                 'Cyprus': {'NAME': {'title_en': 'Cyprus', 'title_ru': 'Кипр'}, 'COUNTRY_FLAG': "sprite-flag_cyprus"},
                 'Czech Republic': {'NAME': {'title_en': 'Czech Republic', 'title_ru': 'Чешская республика'}, 'COUNTRY_FLAG': "sprite-flag_czech_republic"},
                 'Denmark': {'NAME': {'title_en': 'Denmark', 'title_ru': 'Дания'}, 'COUNTRY_FLAG': "sprite-flag_denmark"},
                 'Djibouti': {'NAME': {'title_en': 'Djibouti', 'title_ru': 'Джибути'}, 'COUNTRY_FLAG': "sprite-flag_djibouti"},
                 'Dominica': {'NAME': {'title_en': 'Dominica', 'title_ru': 'Доминика'}, 'COUNTRY_FLAG': "sprite-flag_dominica"},
                 'Dominican Republic': {'NAME': {'title_en': 'Dominican Republic', 'title_ru': 'Доминиканская Республика'}, 'COUNTRY_FLAG': "sprite-flag_dominican_republic"},
                 'East Timor': {'NAME': {'title_en': 'East Timor', 'title_ru': 'Восточный Тимор'}, 'COUNTRY_FLAG': "sprite-flag_east_timor"},
                 'Egypt': {'NAME': {'title_en': 'Egypt', 'title_ru': 'Египет'}, 'COUNTRY_FLAG': "sprite-flag_egypt"},
                 'El Salvador': {'NAME': {'title_en': 'El Salvador', 'title_ru': 'Сальвадор'}, 'COUNTRY_FLAG': "sprite-flag_el_salvador"},
                 'Ecuador': {'NAME': {'title_en': 'Ecuador', 'title_ru': 'Эквадор'}, 'COUNTRY_FLAG': "sprite-flag_equador"},
                 'Equatorial Guinea': {'NAME': {'title_en': 'Equatorial Guinea', 'title_ru': 'Экваториальная Гвинея'}, 'COUNTRY_FLAG': "sprite-flag_equatorial_guinea"},
                 'Eritrea': {'NAME': {'title_en': 'Eritrea', 'title_ru': 'Эритрея'}, 'COUNTRY_FLAG': "sprite-flag_eritrea"},
                 'Ethiopia': {'NAME': {'title_en': 'Ethiopia', 'title_ru': 'Эфиопия'}, 'COUNTRY_FLAG': "sprite-flag_ethiopia"},
                 'Federated State of Micronesia': {'NAME': {'title_en': 'Federated State of Micronesia', 'title_ru': 'Федеративные Штаты Микронезии'}, 'COUNTRY_FLAG': "sprite-flag_federated_states_of_micronesia"},
                 'Fiji': {'NAME': {'title_en': 'Fiji', 'title_ru': 'Фиджи'}, 'COUNTRY_FLAG': "sprite-flag_fiji"},
                 'Finland': {'NAME': {'title_en': 'Finland', 'title_ru': 'Финляндия'}, 'COUNTRY_FLAG': "sprite-flag_finland"},
                 'France': {'NAME': {'title_en': 'France', 'title_ru': 'Франция'}, 'COUNTRY_FLAG': "sprite-flag_france"},
                 'Gabon': {'NAME': {'title_en': 'Gabon', 'title_ru': 'Габон'}, 'COUNTRY_FLAG': "sprite-flag_gabon"},
                 'Gambia': {'NAME': {'title_en': 'Gambia', 'title_ru': 'Гамбия'}, 'COUNTRY_FLAG': "sprite-flag_gambia"},
                 'Germany': {'NAME': {'title_en': 'Germany', 'title_ru': 'Германия'}, 'COUNTRY_FLAG': "sprite-flag_germany"},
                 'Ghana': {'NAME': {'title_en': 'Ghana', 'title_ru': 'Гана'}, 'COUNTRY_FLAG': "sprite-flag_ghana"},
                 'Greece': {'NAME': {'title_en': 'Greece', 'title_ru': 'Греция'}, 'COUNTRY_FLAG': "sprite-flag_greece"},
                 'Grenada': {'NAME': {'title_en': 'Grenada', 'title_ru': 'Гренада'}, 'COUNTRY_FLAG': "sprite-flag_grenada"},
                 'Guatemala': {'NAME': {'title_en': 'Guatemala', 'title_ru': 'Гватемала'}, 'COUNTRY_FLAG': "sprite-flag_guatemala"},
                 'Guinea': {'NAME': {'title_en': 'Guinea', 'title_ru': 'Гвинея'}, 'COUNTRY_FLAG': "sprite-flag_guinea"},
                 'Guinea Bissau': {'NAME': {'title_en': 'Guinea Bissau', 'title_ru': 'Гвинея-Бисау'}, 'COUNTRY_FLAG': "sprite-flag_guinea_bissau"},
                 'Guyana': {'NAME': {'title_en': 'Guyana', 'title_ru': 'Гайана'}, 'COUNTRY_FLAG': "sprite-flag_guyana"},
                 'Haiti': {'NAME': {'title_en': 'Haiti', 'title_ru': 'Гаити'}, 'COUNTRY_FLAG': "sprite-flag_haiti"},
                 'Honduras': {'NAME': {'title_en': 'Honduras', 'title_ru': 'Гондурас'}, 'COUNTRY_FLAG': "sprite-flag_honduras"},
                 'Hungary': {'NAME': {'title_en': 'Hungary', 'title_ru': 'Венгрия'}, 'COUNTRY_FLAG': "sprite-flag_hungary"},
                 'Iceland': {'NAME': {'title_en': 'Iceland', 'title_ru': 'Исландия'}, 'COUNTRY_FLAG': "sprite-flag_iceland"},
                 'India': {'NAME': {'title_en': 'India', 'title_ru': 'Индия'}, 'COUNTRY_FLAG': "sprite-flag_india"},
                 'Indonesia': {'NAME': {'title_en': 'Indonesia', 'title_ru': 'Индонезия'}, 'COUNTRY_FLAG': "sprite-flag_indonesia"},
                 'Iran': {'NAME': {'title_en': 'Iran', 'title_ru': 'Иран'}, 'COUNTRY_FLAG': "sprite-flag_iran"},
                 'Iraq': {'NAME': {'title_en': 'Iraq', 'title_ru': 'Ирак'}, 'COUNTRY_FLAG': "sprite-flag_iraq"},
                 'Ireland': {'NAME': {'title_en': 'Ireland', 'title_ru': 'Ирландия'}, 'COUNTRY_FLAG': "sprite-flag_ireland"},
                 'Italy': {'NAME': {'title_en': 'Italy', 'title_ru': 'Италия'}, 'COUNTRY_FLAG': "sprite-flag_italy"},
                 'Jamaica': {'NAME': {'title_en': 'Jamaica', 'title_ru': 'Ямайка'}, 'COUNTRY_FLAG': "sprite-flag_jamaica"},
                 'Japan': {'NAME': {'title_en': 'Japan', 'title_ru': 'Япония'}, 'COUNTRY_FLAG': "sprite-flag_japan"},
                 'Jordan': {'NAME': {'title_en': 'Jordan', 'title_ru': 'Иордания'}, 'COUNTRY_FLAG': "sprite-flag_jordan"},
                 'Kenya': {'NAME': {'title_en': 'Kenya', 'title_ru': 'Кения'}, 'COUNTRY_FLAG': "sprite-flag_kenya"},
                 'Kiribati': {'NAME': {'title_en': 'Kiribati', 'title_ru': 'Кирибати'}, 'COUNTRY_FLAG': "sprite-flag_kiribati"},
                 'Kuwait': {'NAME': {'title_en': 'Kuwait', 'title_ru': 'Кувейт'}, 'COUNTRY_FLAG': "sprite-flag_kuwait"},
                 'Laos': {'NAME': {'title_en': 'Laos', 'title_ru': 'Лаос'}, 'COUNTRY_FLAG': "sprite-flag_laos"},
                 'Lebanon': {'NAME': {'title_en': 'Lebanon', 'title_ru': 'Ливан'}, 'COUNTRY_FLAG': "sprite-flag_lebanon"},
                 'Lesotho': {'NAME': {'title_en': 'Lesotho', 'title_ru': 'Лесото'}, 'COUNTRY_FLAG': "sprite-flag_lesotho"},
                 'Liberia': {'NAME': {'title_en': 'Liberia', 'title_ru': 'Либерия'}, 'COUNTRY_FLAG': "sprite-flag_liberia"},
                 'Libya': {'NAME': {'title_en': 'Libya', 'title_ru': 'Ливия'}, 'COUNTRY_FLAG': "sprite-flag_libya"},
                 'Liechtenstein': {'NAME': {'title_en': 'Liechtenstein', 'title_ru': 'Лихтенштейн'}, 'COUNTRY_FLAG': "sprite-flag_liechtenstein"},
                 'Luxembourg': {'NAME': {'title_en': 'Luxembourg', 'title_ru': 'Люксембург'}, 'COUNTRY_FLAG': "sprite-flag_luxembourg"},
                 'Macedonia': {'NAME': {'title_en': 'Macedonia', 'title_ru': 'Македония'}, 'COUNTRY_FLAG': "sprite-flag_macedonia"},
                 'Madagascar': {'NAME': {'title_en': 'Madagascar', 'title_ru': 'Мадагаскар'}, 'COUNTRY_FLAG': "sprite-flag_madagascar"},
                 'Malawi': {'NAME': {'title_en': 'Malawi', 'title_ru': 'Малави'}, 'COUNTRY_FLAG': "sprite-flag_malawi"},
                 'Malaysia': {'NAME': {'title_en': 'Malaysia', 'title_ru': 'Малайзия'}, 'COUNTRY_FLAG': "sprite-flag_malaysia"},
                 'Maldives': {'NAME': {'title_en': 'Maldives', 'title_ru': 'Мальдивы'}, 'COUNTRY_FLAG': "sprite-flag_maledives"},
                 'Mali': {'NAME': {'title_en': 'Mali', 'title_ru': 'Мали'}, 'COUNTRY_FLAG': "sprite-flag_mali"},
                 'Malta': {'NAME': {'title_en': 'Malta', 'title_ru': 'Мальта'}, 'COUNTRY_FLAG': "sprite-flag_malta"},
                 'Marshall Islands': {'NAME': {'title_en': 'Marshall Islands', 'title_ru': 'Маршалловы острова'}, 'COUNTRY_FLAG': "sprite-flag_marshall_islands"},
                 'Mauretania': {'NAME': {'title_en': 'Mauretania', 'title_ru': 'Мавритания'}, 'COUNTRY_FLAG': "sprite-flag_mauretania"},
                 'Mauritius': {'NAME': {'title_en': 'Mauritius', 'title_ru': 'Маврикий'}, 'COUNTRY_FLAG': "sprite-flag_mauritius"},
                 'Mexico': {'NAME': {'title_en': 'Mexico', 'title_ru': 'Мексика'}, 'COUNTRY_FLAG': "sprite-flag_mexico"},
                 'Monaco': {'NAME': {'title_en': 'Monaco', 'title_ru': 'Монако'}, 'COUNTRY_FLAG': "sprite-flag_monaco"},
                 'Mongolia': {'NAME': {'title_en': 'Mongolia', 'title_ru': 'Монголия'}, 'COUNTRY_FLAG': "sprite-flag_mongolia"},
                 'Montenegro': {'NAME': {'title_en': 'Montenegro', 'title_ru': 'Черногория'}, 'COUNTRY_FLAG': "sprite-flag_montenegro"},
                 'Morocco': {'NAME': {'title_en': 'Morocco', 'title_ru': 'Марокко'}, 'COUNTRY_FLAG': "sprite-flag_morocco"},
                 'Mozambique': {'NAME': {'title_en': 'Mozambique', 'title_ru': 'Мозамбик'}, 'COUNTRY_FLAG': "sprite-flag_mozambique"},
                 'Myanmar': {'NAME': {'title_en': 'Myanmar', 'title_ru': 'Мьянма'}, 'COUNTRY_FLAG': "sprite-flag_myanmar"},
                 'Namibia': {'NAME': {'title_en': 'Namibia', 'title_ru': 'Намибия'}, 'COUNTRY_FLAG': "sprite-flag_namibia"},
                 'Nauru': {'NAME': {'title_en': 'Nauru', 'title_ru': 'Науру'}, 'COUNTRY_FLAG': "sprite-flag_nauru"},
                 'Nepal': {'NAME': {'title_en': 'Nepal', 'title_ru': 'Непал'}, 'COUNTRY_FLAG': "sprite-flag_nepal"},
                 'Netherlands': {'NAME': {'title_en': 'Netherlands', 'title_ru': 'Нидерланды'}, 'COUNTRY_FLAG': "sprite-flag_netherlands"},
                 'New Zealand': {'NAME': {'title_en': 'New Zealand', 'title_ru': 'Новая Зеландия'}, 'COUNTRY_FLAG': "sprite-flag_new_zealand"},
                 'Nicaragua': {'NAME': {'title_en': 'Nicaragua', 'title_ru': 'Никарагуа'}, 'COUNTRY_FLAG': "sprite-flag_nicaragua"},
                 'Niger': {'NAME': {'title_en': 'Niger', 'title_ru': 'Нигер'}, 'COUNTRY_FLAG': "sprite-flag_niger"},
                 'Nigeria': {'NAME': {'title_en': 'Nigeria', 'title_ru': 'Нигерия'}, 'COUNTRY_FLAG': "sprite-flag_nigeria"},
                 'Niue': {'NAME': {'title_en': 'Niue', 'title_ru': 'Ниуэ'}, 'COUNTRY_FLAG': "sprite-flag_niue"},
                 'North Korea': {'NAME': {'title_en': 'North Korea', 'title_ru': 'Северная Корея'}, 'COUNTRY_FLAG': "sprite-flag_north_korea"},
                 'Norway': {'NAME': {'title_en': 'Norway', 'title_ru': 'Норвегия'}, 'COUNTRY_FLAG': "sprite-flag_norway"},
                 'Oman': {'NAME': {'title_en': 'Oman', 'title_ru': 'Оман'}, 'COUNTRY_FLAG': "sprite-flag_oman"},
                 'Pakistan': {'NAME': {'title_en': 'Pakistan', 'title_ru': 'Пакистан'}, 'COUNTRY_FLAG': "sprite-flag_pakistan"},
                 'Palau': {'NAME': {'title_en': 'Palau', 'title_ru': 'Палау'}, 'COUNTRY_FLAG': "sprite-flag_palau"},
                 'Palestine': {'NAME': {'title_en': 'Palestine', 'title_ru': 'Палестина'}, 'COUNTRY_FLAG': "sprite-flag_palestine"},
                 'Panama': {'NAME': {'title_en': 'Panama', 'title_ru': 'Панама'}, 'COUNTRY_FLAG': "sprite-flag_panama"},
                 'Papua New Guinea': {'NAME': {'title_en': 'Papua New Guinea', 'title_ru': 'Папуа-Новая Гвинея'}, 'COUNTRY_FLAG': "sprite-flag_papua_new_guinea"},
                 'Paraguay': {'NAME': {'title_en': 'Paraguay', 'title_ru': 'Парагвай'}, 'COUNTRY_FLAG': "sprite-flag_paraquay"},
                 'Peru': {'NAME': {'title_en': 'Peru', 'title_ru': 'Перу'}, 'COUNTRY_FLAG': "sprite-flag_peru"},
                 'Philippines': {'NAME': {'title_en': 'Philippines', 'title_ru': 'Филиппины'}, 'COUNTRY_FLAG': "sprite-flag_philippines"},
                 'Poland': {'NAME': {'title_en': 'Poland', 'title_ru': 'Польша'}, 'COUNTRY_FLAG': "sprite-flag_poland"},
                 'Portugal': {'NAME': {'title_en': 'Portugal', 'title_ru': 'Португалия'}, 'COUNTRY_FLAG': "sprite-flag_portugal"},
                 'Qatar': {'NAME': {'title_en': 'Qatar', 'title_ru': 'Катар'}, 'COUNTRY_FLAG': "sprite-flag_qatar"},
                 'Romania': {'NAME': {'title_en': 'Romania', 'title_ru': 'Румыния'}, 'COUNTRY_FLAG': "sprite-flag_romania"},
                 'Rwanda': {'NAME': {'title_en': 'Rwanda', 'title_ru': 'Руанда'}, 'COUNTRY_FLAG': "sprite-flag_rwanda"},
                 'Saint Kitts and Nevis': {'NAME': {'title_en': 'Saint Kitts and Nevis', 'title_ru': 'Сент-Китс и Невис'}, 'COUNTRY_FLAG': "sprite-flag_saint_kitts_and_nevis"},
                 'Saint Lucia': {'NAME': {'title_en': 'Saint Lucia', 'title_ru': 'Сент-Люсия'}, 'COUNTRY_FLAG': "sprite-flag_saint_lucia"},
                 'Saint Vincent and the Grenadines': {'NAME': {'title_en': 'Saint Vincent and the Grenadines', 'title_ru': 'Сент-Винсент и Гренадины'}, 'COUNTRY_FLAG': "sprite-flag_saint_vincent_and_the_grenadines"},
                 'Samoa': {'NAME': {'title_en': 'Samoa', 'title_ru': 'Самоа'}, 'COUNTRY_FLAG': "sprite-flag_samoa"},
                 'San Marino': {'NAME': {'title_en': 'San Marino', 'title_ru': 'Сан - Марино'}, 'COUNTRY_FLAG': "sprite-flag_san_marino"},
                 'Sao Tome and Principe': {'NAME': {'title_en': 'Sao Tome and Principe', 'title_ru': 'Сан-Томе и Принсипи'}, 'COUNTRY_FLAG': "sprite-flag_sao_tome_and_principe"},
                 'Saudi Arabia': {'NAME': {'title_en': 'Saudi Arabia', 'title_ru': 'Саудовская Аравия'}, 'COUNTRY_FLAG': "sprite-flag_saudi_arabia"},
                 'Senegal': {'NAME': {'title_en': 'Senegal', 'title_ru': 'Сенегал'}, 'COUNTRY_FLAG': "sprite-flag_senegal"},
                 'Serbia': {'NAME': {'title_en': 'Serbia', 'title_ru': 'Сербия'}, 'COUNTRY_FLAG': "sprite-flag_serbia"},
                 'Seychelles': {'NAME': {'title_en': 'Seychelles', 'title_ru': 'Сейшельские острова'}, 'COUNTRY_FLAG': "sprite-flag_seychelles"},
                 'Sierra Leone': {'NAME': {'title_en': 'Sierra Leone', 'title_ru': 'Сьерра-Леоне'}, 'COUNTRY_FLAG': "sprite-flag_sierra_leone"},
                 'Singapore': {'NAME': {'title_en': 'Singapore', 'title_ru': 'Сингапур'}, 'COUNTRY_FLAG': "sprite-flag_singapore"},
                 'Slovakia': {'NAME': {'title_en': 'Slovakia', 'title_ru': 'Словакия'}, 'COUNTRY_FLAG': "sprite-flag_slovakia"},
                 'Slovenia': {'NAME': {'title_en': 'Slovenia', 'title_ru': 'Словения'}, 'COUNTRY_FLAG': "sprite-flag_slovenia"},
                 'Solomon Islands': {'NAME': {'title_en': 'Solomon Islands', 'title_ru': 'Соломоновы Острова'}, 'COUNTRY_FLAG': "sprite-flag_solomon_islands"},
                 'Somalia': {'NAME': {'title_en': 'Somalia', 'title_ru': 'Сомали'}, 'COUNTRY_FLAG': "sprite-flag_somalia"},
                 'South Africa': {'NAME': {'title_en': 'South Africa', 'title_ru': 'ЮАР'}, 'COUNTRY_FLAG': "sprite-flag_south_africa"},
                 'South Korea': {'NAME': {'title_en': 'South Korea', 'title_ru': 'Южная Корея'}, 'COUNTRY_FLAG': "sprite-flag_south_korea"},
                 'South Sudan': {'NAME': {'title_en': 'South Sudan', 'title_ru': 'Южный Судан'}, 'COUNTRY_FLAG': "sprite-flag_south_sudan"},
                 'Spain': {'NAME': {'title_en': 'Spain', 'title_ru': 'Испания'}, 'COUNTRY_FLAG': "sprite-flag_spain"},
                 'Sri Lanka': {'NAME': {'title_en': 'Sri Lanka', 'title_ru': 'Шри Ланка'}, 'COUNTRY_FLAG': "sprite-flag_sri_lanka"},
                 'Sudan': {'NAME': {'title_en': 'Sudan', 'title_ru': 'Судан'}, 'COUNTRY_FLAG': "sprite-flag_sudan"},
                 'Suriname': {'NAME': {'title_en': 'Suriname', 'title_ru': 'Суринам'}, 'COUNTRY_FLAG': "sprite-flag_suriname"},
                 'Swaziland': {'NAME': {'title_en': 'Swaziland', 'title_ru': 'Свазиленд'}, 'COUNTRY_FLAG': "sprite-flag_swaziland"},
                 'Sweden': {'NAME': {'title_en': 'Sweden', 'title_ru': 'Швеция'}, 'COUNTRY_FLAG': "sprite-flag_sweden"},
                 'Switzerland': {'NAME': {'title_en': 'Switzerland', 'title_ru': 'Швейцария'}, 'COUNTRY_FLAG': "sprite-flag_switzerland"},
                 'Syria': {'NAME': {'title_en': 'Syria', 'title_ru': 'Сирия'}, 'COUNTRY_FLAG': "sprite-flag_syria"},
                 'Tanzania': {'NAME': {'title_en': 'Tanzania', 'title_ru': 'Танзания'}, 'COUNTRY_FLAG': "sprite-flag_tanzania"},
                 'Thailand': {'NAME': {'title_en': 'Thailand', 'title_ru': 'Таиланд'}, 'COUNTRY_FLAG': "sprite-flag_thailand"},
                 'Togo': {'NAME': {'title_en': 'Togo', 'title_ru': 'Того'}, 'COUNTRY_FLAG': "sprite-flag_togo"},
                 'Tonga': {'NAME': {'title_en': 'Tonga', 'title_ru': 'Тонга'}, 'COUNTRY_FLAG': "sprite-flag_tonga"},
                 'Trinidad and Tobago': {'NAME': {'title_en': 'Trinidad and Tobago', 'title_ru': 'Тринидад и Тобаго'}, 'COUNTRY_FLAG': "sprite-flag_trinidad_and_tobago"},
                 'Tunisia': {'NAME': {'title_en': 'Tunisia', 'title_ru': 'Тунис'}, 'COUNTRY_FLAG': "sprite-flag_tunisia"},
                 'Turkey': {'NAME': {'title_en': 'Turkey', 'title_ru': 'Турция'}, 'COUNTRY_FLAG': "sprite-flag_turkey"},
                 'Tuvalu': {'NAME': {'title_en': 'Tuvalu', 'title_ru': 'Тувалу'}, 'COUNTRY_FLAG': "sprite-flag_tuvalu"},
                 'Uganda': {'NAME': {'title_en': 'Uganda', 'title_ru': 'Уганда'}, 'COUNTRY_FLAG': "sprite-flag_uganda"},
                 'United Arab Emirates': {'NAME': {'title_en': 'United Arab Emirates', 'title_ru': 'Объединенные Арабские Эмираты'}, 'COUNTRY_FLAG': "sprite-flag_united_arab_emirates"},
                 'United Kingdom': {'NAME': {'title_en': 'United Kingdom', 'title_ru': 'Великобритания'}, 'COUNTRY_FLAG': "sprite-flag_united_kingdom"},
                 'Uruguay': {'NAME': {'title_en': 'Uruguay', 'title_ru': 'Уругвай'}, 'COUNTRY_FLAG': "sprite-flag_uruquay"},
                 'USA': {'NAME': {'title_en': 'USA', 'title_ru': 'США'}, 'COUNTRY_FLAG': "sprite-flag_usa"},
                 'Vanuatu': {'NAME': {'title_en': 'Vanuatu', 'title_ru': 'Вануату'}, 'COUNTRY_FLAG': "sprite-flag_vanuatu"},
                 'Vatican City': {'NAME': {'title_en': 'Vatican City', 'title_ru': 'Ватикан'}, 'COUNTRY_FLAG': "sprite-flag_vatican_city"},
                 'Venezuela': {'NAME': {'title_en': 'Venezuela', 'title_ru': 'Венесуэла'}, 'COUNTRY_FLAG': "sprite-flag_venezuela"},
                 'Vietnam': {'NAME': {'title_en': 'Vietnam', 'title_ru': 'Вьетнам'}, 'COUNTRY_FLAG': "sprite-flag_vietnam"},
                 'Yemen': {'NAME': {'title_en': 'Yemen', 'title_ru': 'Йемен'}, 'COUNTRY_FLAG': "sprite-flag_yemen"},
                 'Zambia': {'NAME': {'title_en': 'Zambia', 'title_ru': 'Замбия'}, 'COUNTRY_FLAG': "sprite-flag_zambia"},
                 'Zimbabwe': {'NAME': {'title_en': 'Zimbabwe', 'title_ru': 'Зимбабве'}, 'COUNTRY_FLAG': "sprite-flag_zimbabwe"},

    }

    for title, attr in countries.items():
        cntr, res = Country.objects.get_or_create(title=title, create_user=crt_usr)
        if res:
            cntr.setAttributeValue({'NAME': attr['NAME']}, crt_usr)
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