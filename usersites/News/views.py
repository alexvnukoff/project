from haystack.backends import SQ
from appl import func
from appl.func import getActiveSQS, setPaginationForSearchWithValues, getPaginatorRange
from appl.models import News, UserSites, Gallery
from core.models import Item
from django.core.exceptions import ObjectDoesNotExist
from django.http import  HttpResponse, HttpResponseNotFound
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _
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
     new = get_object_or_404(News, pk=item_id)
     newValues = new.getAttributeValues(*('NAME', 'DETAIL_TEXT', 'YOUTUBE_CODE', 'IMAGE'))
     description = newValues.get('DETAIL_TEXT', False)[0] if newValues.get('DETAIL_TEXT', False) else ""
     photos = Gallery.objects.filter(c2p__parent=new)






     template = loader.get_template('News/detailContent.html')

     templateParams = {
       'newValues': newValues,
       'photos': photos,
       'item_id': item_id,
      }

     context = RequestContext(request, templateParams)
     rendered = template.render(context)




     return rendered
















