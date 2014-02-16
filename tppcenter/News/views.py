from django.shortcuts import render
from django.shortcuts import render_to_response
from appl.models import *
from django.http import Http404, HttpResponseRedirect
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

from core.tasks import addNewsAttrubute
from django.conf import settings

def get_news_list(request, page=1):
    user = request.user
    if not user.first_name and not user.last_name:
        user_name = user.email
    else:
        user_name = user.first_name + ' ' + user.last_name

    current_section = "News"

    newsPage = _newsContent(request, page)

    notification = len(Notification.objects.filter(user=request.user, read=False))




    return render_to_response("News/index.html", {'user_name': user_name, 'current_section': current_section,
                                                  'newsPage': newsPage, 'notification': notification},
                              context_instance=RequestContext(request))


def _newsContent(request, page=1):
    news = News.active.get_active().order_by('-pk')


    result = func.setPaginationForItemsWithValues(news, *('NAME', 'IMAGE', 'DETAIL_TEXT'), page_num=5, page=page)

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
    query_string = {'next': 23, 'alo': 45, 'privet': 34}


    url_paginator = "news:paginator"
    template = loader.get_template('News/contentPage.html')
    context = RequestContext(request, {'newsList': newsList, 'page': page, 'paginator_range': paginator_range,
                                                  'url_paginator': url_paginator, 'query_string': query_string})
    return template.render(context)






def addNews(request):
    form = None

    if request.POST:
        func.notify("item_creating", 'notification', user=request.user)
        user = request.user
        user = request.user
        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
        gallery = Photo(request.POST, request.FILES)

        values = {}
        values['NAME'] = request.POST.get('NAME', "")
        values['DETAIL_TEXT'] = request.POST.get('DETAIL_TEXT', "")
        values['IMAGE'] = request.FILES.get('IMAGE', "")

        form = ItemForm('News', values=values)
        form.clean()

        if gallery.is_valid() and form.is_valid():
            addNewsAttrubute.delay(request.POST, request.FILES, user, settings.SITE_ID)
            return HttpResponseRedirect(reverse('news:main'))





    return render_to_response('News/addForm.html', {'form': form}, context_instance=RequestContext(request))



def updateNew(request, item_id):

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
        values['IMAGE'] = request.FILES.get('IMAGE', "")

        form = ItemForm('News', values=values, id=item_id)
        form.clean()

        if gallery.is_valid() and form.is_valid():
            addNewsAttrubute.delay(request.POST, request.FILES, user, settings.SITE_ID, item_id)
            return HttpResponseRedirect(reverse('news:main'))







    return render_to_response('News/addForm.html', {'gallery': gallery, 'photos': photos, 'form': form}, context_instance=RequestContext(request))



