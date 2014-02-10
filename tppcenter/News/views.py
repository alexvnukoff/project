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

def get_news_list(request, page=1):
    user = request.user
    if not user.first_name and not user.last_name:
        user_name = user.email
    else:
        user_name = user.first_name + ' ' + user.last_name

    current_section = "News"



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


    url_paginator = "news:paginator"


    return render_to_response("News/index.html", {'newsList': newsList, 'page': page, 'paginator_range': paginator_range,
                                                  'url_paginator': url_paginator, 'user_name': user_name,
                                                  'current_section': current_section})









