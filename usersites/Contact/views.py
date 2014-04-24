from urllib.parse import urlencode
from django.http.response import HttpResponsePermanentRedirect
from haystack.backends import SQ
from appl import func
from appl.func import getActiveSQS, setPaginationForSearchWithValues, getPaginatorRange
from appl.models import News, Organization, NewsCategories, Gallery, Country, UserSites
from core.models import Item, Group
from datetime import datetime
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.syndication.views import Feed
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound, HttpResponseGone
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.utils.feedgenerator import Rss201rev2Feed
from django.utils.translation import ugettext as _
from django.utils.timezone import now
import tppcenter
from tppcenter.forms import ItemForm,BasePhotoGallery
from pytz import timezone
import pytz
import json
import requests
from django.contrib.sites.models import Site


from core.tasks import addNewsAttrubute
from django.conf import settings

def get_news_list(request, page=1, item_id=None, my=None, slug=None):


    if item_id:
       if not Item.active.get_active().filter(pk=item_id).exists():
         return HttpResponseNotFound()




    try:
        if not item_id:

            contentPage = _get_content(request, page)

        else:
            contentPage = _getdetailcontent(request, item_id, slug)
            if isinstance(contentPage, HttpResponse):
                return contentPage

            add_news = True

    except ObjectDoesNotExist:
        contentPage = func.emptyCompany()





    current_section = _("News")
    title = _("News")

    templateParams = {
    'current_section': current_section,
    'contentPage': contentPage,
    'title': title
    }

    return render_to_response("index.html", templateParams, context_instance=RequestContext(request))








def _get_content(request, page):
     user_site = UserSites.objects.get(sites__id=settings.SITE_ID)
     organization = user_site.organization.pk

     sqs = getActiveSQS().models(News).filter(SQ(tpp=organization) |
                                              SQ(company=organization)).order_by('-obj_create_date')

     url_paginator = 'news:paginator'

     attr = ('NAME', 'IMAGE', 'DETAIL_TEXT', 'SLUG', 'ANONS')

     result = setPaginationForSearchWithValues(sqs, *attr, page_num=10, page=page)

     content = result[0]

     page = result[1]

     paginator_range = getPaginatorRange(page)

     templateParams = {
         'url_paginator': url_paginator,
         'content': content,
         'page': page,
         'paginator_range': paginator_range

     }

     template = loader.get_template('News/contentPage.html')
     context = RequestContext(request, templateParams)
     rendered = template.render(context)

     return rendered













def _getdetailcontent(request, item_id, slug):
    prefix =  Site.objects.get(name='tppcenter').domain + '/'# Note, you need the trailing slash

    url = (reverse(viewname='news:detail' ,urlconf=tppcenter.urls,  args=[slug], prefix=prefix))
    url = requests.get("http://"+ url)


    return HttpResponse(url)














