from django.shortcuts import render
from django.shortcuts import render_to_response, get_object_or_404
from appl.models import *
from django.http import Http404, HttpResponseRedirect, HttpResponse
from core.models import Value, Item, Attribute, Dictionary, AttrTemplate, Relationship
from appl import func
from django.core.exceptions import ValidationError
from django.forms.models import modelformset_factory
from django.db.models import get_app, get_models
from tppcenter.forms import ItemForm, Test, BasePhotoGallery
from django.template import RequestContext, loader
from datetime import datetime
from django.utils.timezone import now
from django.core.urlresolvers import reverse
from tpp.SiteUrlMiddleWare import get_request
from celery import shared_task, task
from haystack.query import SQ, SearchQuerySet
import json
from django.core.exceptions import ObjectDoesNotExist


from core.tasks import addNewsAttrubute
from django.conf import settings

def get_news_list(request, page=1):

    newsPage = _newsContent(request, page)

    styles = []
    scripts = []

    if not request.is_ajax():
        user = request.user
        if user.is_authenticated():
            notification = len(Notification.objects.filter(user=request.user, read=False))
            if not user.first_name and not user.last_name:
                user_name = user.email
            else:
                user_name = user.first_name + ' ' + user.last_name
        else:
            user_name = None
            notification = None
        current_section = "News"

        tempalteParams = {
            'user_name': user_name,
            'current_section': current_section,
            'notification': notification,
            'newsPage': newsPage,
            'scripts': scripts,
            'styles': styles,
            'search': request.GET.get('q', '')
        }

        return render_to_response("News/index.html", tempalteParams, context_instance=RequestContext(request))
    else:
        return HttpResponse(json.dumps({'styles': styles, 'scripts': scripts, 'content': newsPage}))

def _newsContent(request, page=1):

    filters, searchFilter = func.filterLive(request)

    #news = News.active.get_active().order_by('-pk')

    sqs = SearchQuerySet().models(News)

    if len(searchFilter) > 0:
        sqs = sqs.filter(**searchFilter)

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

    result = func.setPaginationForSearchWithValues(news, *('NAME', 'IMAGE', 'DETAIL_TEXT', 'SLUG'), page_num=5, page=page)
    #result = func.setPaginationForItemsWithValues(news, *('NAME', 'IMAGE', 'DETAIL_TEXT', 'SLUG'), page_num=5, page=page)

    newsList = result[0]
    news_ids = [id for id in newsList.keys()]

    func.addDictinoryWithCountryAndOrganization(news_ids, newsList)

    page = result[1]
    paginator_range = func.getPaginatorRange(page)



    url_paginator = "news:paginator"
    template = loader.get_template('News/contentPage.html')

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
    return template.render(context)






def addNews(request):
    form = None

    categories = func.getItemsList('NewsCategories', 'NAME')


    if request.POST:
        func.notify("item_creating", 'notification', user=request.user)
        user = request.user
        user = request.user
        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
        gallery = Photo(request.POST, request.FILES)

        values = {}
        values['NAME'] = request.POST.get('NAME', "")
        values['DETAIL_TEXT'] = request.POST.get('DETAIL_TEXT', "")
        values['YOUTUBE_CODE'] = request.POST.get('YOUTUBE_CODE', "")
        values['IMAGE'] = request.FILES.get('IMAGE', "")


        form = ItemForm('News', values=values)
        form.clean()

        if gallery.is_valid() and form.is_valid():
            addNewsAttrubute.delay(request.POST, request.FILES, user, settings.SITE_ID)
            return HttpResponseRedirect(reverse('news:main'))





    return render_to_response('News/addForm.html', {'form': form, 'categories': categories}, context_instance=RequestContext(request))



def updateNew(request, item_id):

    try:
        choosen_category = NewsCategories.objects.get(p2c__child__id=item_id)
    except ObjectDoesNotExist:
        choosen_category = ''
    categories = func.getItemsList('NewsCategories', 'NAME')
    if request.method != 'POST':
        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
        gallery = Photo(parent_id=item_id)
        photos = ""

        if gallery.queryset:
            photos = [{'photo': image.photo, 'pk': image.pk} for image in gallery.queryset]


        form = ItemForm('News', id=item_id)

    if request.POST:
        func.notify("item_creating", 'notification', user=request.user)

        user = request.user
        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
        gallery = Photo(request.POST, request.FILES)

        values = {}
        values['NAME'] = request.POST.get('NAME', "")
        values['DETAIL_TEXT'] = request.POST.get('DETAIL_TEXT', "")
        values['YOUTUBE_CODE'] = request.POST.get('YOUTUBE_CODE', "")
        values['IMAGE'] = request.FILES.get('IMAGE', "")
        values['IMAGE-CLEAR'] = request.POST.get('IMAGE-CLEAR', " ")

        form = ItemForm('News', values=values, id=item_id)
        form.clean()

        if gallery.is_valid() and form.is_valid():
            addNewsAttrubute.delay(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id)
            return HttpResponseRedirect(reverse('news:main'))







    return render_to_response('News/addForm.html', {'gallery': gallery, 'photos': photos, 'form': form,
                                                    'choosen_category': choosen_category, 'categories': categories},
                              context_instance=RequestContext(request))



def detail(request, item_id):

    styles = [settings.STATIC_URL + 'tppcenter/css/news.css', settings.STATIC_URL + 'tppcenter/css/company.css']
    scripts = []

    user = request.user
    if user.is_authenticated():
        notification = len(Notification.objects.filter(user=request.user, read=False))
        if not user.first_name and not user.last_name:
            user_name = user.email
        else:
            user_name = user.first_name + ' ' + user.last_name
    else:
        user_name = None
        notification = None
    current_section = "News"



    newsPage = _getdetailcontent(request, item_id)


    templateParams = {
        'user_name': user_name,
        'current_section': current_section,
        'newsPage': newsPage,
        'notification': notification,
        'styles': styles,
        'scripts': scripts
    }



    return render_to_response("News/index.html", templateParams, context_instance=RequestContext(request))



def _getdetailcontent(request, id):
    new = get_object_or_404(News, pk=id)
    newValues = new.getAttributeValues(*('NAME', 'DETAIL_TEXT', 'YOUTUBE_CODE', 'IMAGE'))
    photos = Gallery.objects.filter(c2p__parent=new)
    organizations = dict(Organization.objects.filter(p2c__child=new.pk).values('c2p__parent__country', 'pk'))
    try:
        newsCategory = NewsCategories.objects.get(p2c__child=id)
        category_value = newsCategory.getAttributeValues('NAME')
        newValues.update({'CATEGORY_NAME': category_value})
        similar_news = News.objects.filter(c2p__parent__id=newsCategory.id).exclude(id=new.id)[:3]
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



    template = loader.get_template('News/detailContent.html')

    context = RequestContext(request, {'newValues': newValues, 'photos': photos, 'similarValues': similarValues})
    return template.render(context)
