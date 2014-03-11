from django.shortcuts import render_to_response, get_object_or_404
from appl.models import *

from django.utils.translation import ugettext as _
from django.http import Http404, HttpResponseRedirect, HttpResponse
from core.models import Value, Item, Attribute, Dictionary, AttrTemplate, Relationship

from appl import func
from tppcenter.forms import ItemForm
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from haystack.query import SQ, SearchQuerySet
import json
from core.tasks import addTppAttrubute
from django.conf import settings
from django.utils import timezone
from datetime import datetime

def get_news_list(request,page=1, id=None, slug=None):

    if slug and not Value.objects.filter(item=id, attr__title='SLUG', title=slug).exists():
         slug = Value.objects.get(item=id, attr__title='SLUG').title
         return HttpResponseRedirect(reverse('tv:detail',  args=[slug]))

    cabinetValues = func.getB2BcabinetValues(request)

    filterAdv = []

    cabinetValues = func.getB2BcabinetValues(request)

    current_company = request.session.get('current_company', False)

    if current_company:
        current_company = Organization.objects.get(pk=current_company).getAttributeValues("NAME")

    current_section = _("TPP-TV")

    styles = [settings.STATIC_URL + 'tppcenter/css/news.css']
    scripts = []


    if not id:
        newsPage, filterAdv = _newsContent(request, page)
    else:
        newsPage, filterAdv = _getdetailcontent(request, id)

    bRight = func.getBannersRight(request, ['Right 1', 'Right 2'], settings.SITE_ID, 'AdvBanner/banners.html', filter=filterAdv)
    bLeft = func.getBannersRight(request, ['Left 1', 'Left 2', 'Left 3'], settings.SITE_ID, 'AdvBanner/banners.html', filter=filterAdv)
    tops = func.getTops(request, {Product: 5, InnovationProject: 5, Company: 5, BusinessProposal: 5}, filter=filterAdv)


    if not request.is_ajax():

        user = request.user

        if user.is_authenticated():
            notification = Notification.objects.filter(user=request.user, read=False).count()

            if not user.first_name and not user.last_name:
                user_name = user.email
            else:
                user_name = user.first_name + ' ' + user.last_name
        else:
            user_name = None
            notification = None
        current_section = "TPP-TV"

        templatePramrams = {
            'user_name': user_name,
            'current_section': current_section,
            'newsPage': newsPage,
            'notification': notification,
            'scripts': scripts,
            'styles': styles,
            'search': request.GET.get('q', ''),
            'current_company': current_company,
            'addNew': reverse('tv:add'),
            'cabinetValues': cabinetValues,
            'bannerRight': bRight,
            'bannerLeft': bLeft,
            'tops': tops
        }

        return render_to_response("TppTV/index.html", templatePramrams, context_instance=RequestContext(request))

    else:

        serialize = {
            'styles': styles,
            'scripts': scripts,
            'content': newsPage,
            'bannerRight': bRight,
            'bannerLeft': bLeft,
            'tops': tops
        }

        return HttpResponse(json.dumps(serialize))



def _newsContent(request, page=1):

    #news = TppTV.active.get_active().order_by('-pk')

    filters, searchFilter, filterAdv = func.filterLive(request)

    #companies = Company.active.get_active().order_by('-pk')
    sqs = SearchQuerySet().models(TppTV)

    if len(searchFilter) > 0:
        sqs = sqs.filter(**searchFilter).filter(SQ(obj_end_date__gt=timezone.now())| SQ(obj_end_date__exact=datetime(1 , 1, 1)),
                                                               obj_start_date__lt=timezone.now())

    q = request.GET.get('q', '')

    if q != '':
        sqs = sqs.filter(SQ(title=q) | SQ(text=q))

    sortFields = {
        'date': 'id',
        'name': 'title'
    }

    order = []

    sortField1 = request.GET.get('sortField1', 'date')
    sortField2 = request.GET.get('sortField2', None)
    order1 = request.GET.get('order1', 'desc')
    order2 = request.GET.get('order2', None)

    if sortField1 and sortField1 in sortFields:
        if order1 == 'desc':
            order.append('-' + sortFields[sortField1])
        else:
            order.append(sortFields[sortField1])
    else:
        order.append('-id')

    if sortField2 and sortField2 in sortFields:
        if order2 == 'desc':
            order.append('-' + sortFields[sortField2])
        else:
            order.append(sortFields[sortField2])


    news = sqs.order_by(*order)

    result = func.setPaginationForSearchWithValues(news, *('NAME', 'YOUTUBE_CODE', 'SLUG'), page_num=9, page=page)
    #result = func.setPaginationForItemsWithValues(news, *('NAME', 'YOUTUBE_CODE', 'SLUG'), page_num=9, page=page)

    newsList = result[0]
    news_ids = [id for id in newsList.keys()]
    countries = Country.objects.filter(p2c__child__p2c__child__in=news_ids).values('p2c__child__p2c__child', 'pk')
    countries_id = [country['pk'] for country in countries]
    countriesList = Item.getItemsAttributesValues(("NAME", 'FLAG'), countries_id)
    country_dict = {}

    for country in countries:
        country_dict[country['p2c__child__p2c__child']] = country['pk']

    for id, new in newsList.items():
        toUpdate = {'COUNTRY_NAME': countriesList[country_dict[id]].get('NAME', 0) if country_dict.get(id, 0) else [0],
                    'COUNTRY_FLAG': countriesList[country_dict[id]].get('FLAG', 0) if country_dict.get(id, 0) else [0],
                    'COUNTRY_ID':  country_dict.get(id, 0)}
        new.update(toUpdate)

    page = result[1]
    paginator_range = func.getPaginatorRange(page)



    url_paginator = "tv:paginator"
    template = loader.get_template('TppTV/contentPage.html')


    templateParams = {
        'newsList': newsList,
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'filters': filters,
        'sortField1': sortField1,
        'sortField2': sortField2,
        'order1': order1,
        'order2': order2
    }

    context = RequestContext(request, templateParams)

    return template.render(context), filterAdv

@login_required(login_url='/login/')
def tvForm(request, action, item_id=None):
    cabinetValues = func.getB2BcabinetValues(request)

    current_company = request.session.get('current_company', False)
    if current_company:
        current_company = Organization.objects.get(pk=current_company).getAttributeValues("NAME")


    user = request.user

    if user.is_authenticated():
        notification = Notification.objects.filter(user=request.user, read=False).count()

        if not user.first_name and not user.last_name:
            user_name = user.email
        else:
            user_name = user.first_name + ' ' + user.last_name

    else:

        user_name = None
        notification = None

    current_section = _("TppTv")

    if action == 'add':
        newsPage = addNews(request)
    else:
        newsPage = updateNew(request, item_id)

    if isinstance(newsPage, HttpResponseRedirect) or isinstance(newsPage, HttpResponse):
        return newsPage

    return render_to_response('TppTV/index.html', {'newsPage': newsPage, 'current_company':current_company,
                                                              'notification': notification, 'user_name': user_name,
                                                              'current_section': current_section,
                                                              'cabinetValues': cabinetValues},
                              context_instance=RequestContext(request))

def addNews(request):
    current_company = request.session.get('current_company', None)
    perm = request.user.get_all_permissions()
    if not {'appl.add_tpptv'}.issubset(perm):
         return render_to_response("permissionDenied.html")
    form = None

    categories = func.getItemsList('NewsCategories', 'NAME')
    countries = func.getItemsList("Country", 'NAME')


    if request.POST:

        user = request.user
        user = request.user


        values = {}
        values['NAME'] = request.POST.get('NAME', "")
        values['DETAIL_TEXT'] = request.POST.get('DETAIL_TEXT', "")
        values['YOUTUBE_CODE'] = request.POST.get('YOUTUBE_CODE', "")
        values['IMAGE'] = request.FILES.get('IMAGE', "")


        form = ItemForm('TppTV', values=values)
        form.clean()

        if form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addTppAttrubute.delay(request.POST, request.FILES, user, settings.SITE_ID, lang_code=settings.LANGUAGE_CODE)
            return HttpResponseRedirect(reverse('tv:main'))

    template = loader.get_template('TppTV/addForm.html')
    context = RequestContext(request, {'form': form, 'categories': categories, 'countries': countries})
    newsPage = template.render(context)






    return newsPage



def updateNew(request, item_id):

    perm = request.user.get_all_permissions()
    if not {'appl.change_tpptv'}.issubset(perm) or not 'Redactor' in request.user.groups.values_list('name', flat=True):
          return render_to_response("permissionDenied.html")

    create_date = TppTV.objects.get(pk=item_id).create_date

    try:
        choosen_category = NewsCategories.objects.get(p2c__child__id=item_id)
    except ObjectDoesNotExist:
        choosen_category = ''
    try:
        choosen_country = Country.objects.get(p2c__child__id=item_id)
    except ObjectDoesNotExist:
        choosen_country = ""

    countries = func.getItemsList("Country", 'NAME')
    categories = func.getItemsList('NewsCategories', 'NAME')
    if request.method != 'POST':



        form = ItemForm('TppTV', id=item_id)

    if request.POST:


        user = request.user


        values = {}
        values['NAME'] = request.POST.get('NAME', "")
        values['DETAIL_TEXT'] = request.POST.get('DETAIL_TEXT', "")
        values['YOUTUBE_CODE'] = request.POST.get('YOUTUBE_CODE', "")
        values['IMAGE'] = request.FILES.get('IMAGE', "")
        values['IMAGE-CLEAR'] = request.POST.get('IMAGE-CLEAR', " ")

        form = ItemForm('TppTV', values=values, id=item_id)
        form.clean()

        if form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addTppAttrubute.delay(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id, lang_code=settings.LANGUAGE_CODE)
            return HttpResponseRedirect(reverse('tv:main'))


    template = loader.get_template('TppTV/addForm.html')
    context = RequestContext(request, {'form': form, 'choosen_category': choosen_category, 'categories': categories,
                                       'create_date': create_date,'choosen_country':choosen_country,
                                       'countries': countries})
    newsPage = template.render(context)


    return newsPage




def _getdetailcontent(request, id):

    filterAdv = func.getDeatailAdv(id)

    new = get_object_or_404(TppTV, pk=id)
    newValues = new.getAttributeValues(*('NAME', 'DETAIL_TEXT', 'YOUTUBE_CODE'))

    organizations = dict(Organization.objects.filter(p2c__child=new.pk).values('c2p__parent__country', 'pk'))
    try:
        newsCategory = NewsCategories.objects.get(p2c__child=id)
        category_value = newsCategory.getAttributeValues('NAME')
        newValues.update({'CATEGORY_NAME': category_value})
        similar_news = TppTV.objects.filter(c2p__parent__id=newsCategory.id).exclude(id=new.id)[:3]
        similar_news_ids = [sim_news.pk for sim_news in similar_news]
        similarValues = Item.getItemsAttributesValues(('NAME', 'DETAIL_TEXT', 'IMAGE', 'SLUG'), similar_news_ids)
    except ObjectDoesNotExist:
        similarValues = None
        pass


    if organizations.get('c2p__parent__country', False):
        countriesList = Item.getItemsAttributesValues(('NAME', 'FLAG'), organizations['c2p__parent__country'])
        toUpdate = {'COUNTRY_NAME': countriesList[organizations['c2p__parent__country']].get('NAME', [""]),
                    'COUNTRY_FLAG': countriesList[organizations['c2p__parent__country']].get('FLAG', [""]),
                    'COUNTRY_ID': organizations['c2p__parent__country']}
        newValues.update(toUpdate)


    if organizations.get('pk', False):
        organizationsList = Item.getItemsAttributesValues(('NAME', 'FLAG'), organizations['pk'])
        toUpdate = {'ORG_NAME': organizationsList[organizations['pk']].get('NAME', [""]),
                    'ORG_FLAG': organizationsList[organizations['pk']].get('FLAG', [""]),
                    'ORG_ID': organizations['pk']}
        newValues.update(toUpdate)



    template = loader.get_template('TppTV/detailContent.html')

    context = RequestContext(request, {'newValues': newValues, 'similarValues': similarValues})

    return template.render(context), filterAdv
