from haystack.backends import SQ
from appl import func
from appl.func import getActiveSQS, setPaginationForSearchWithValues, getPaginatorRange
from appl.models import Product, UserSites, AdditionalPages, Company, Country, Gallery
from core.models import Item
from django.core.exceptions import ObjectDoesNotExist
from django.http import  HttpResponse, HttpResponseNotFound
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _
from django.conf import settings

def get_products_list(request, page=1, item_id=None, my=None, slug=None):


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





    current_section = _("Products")
    title = _("Products")

    templateParams = {
    'current_section': current_section,
    'contentPage': contentPage,
    'title': title
    }

    return render_to_response("index.html", templateParams, context_instance=RequestContext(request))








def _get_content(request, page):
     user_site = UserSites.objects.get(sites__id=settings.SITE_ID)
     organization = user_site.organization.pk

     sqs = getActiveSQS().models(Product).filter(SQ(tpp=organization) |
                                              SQ(company=organization)).order_by('-obj_create_date')

     url_paginator = 'products:paginator'

     attr = ('NAME', 'COST', 'CURRENCY', 'SLUG', 'IMAGE')

     result = setPaginationForSearchWithValues(sqs, *attr, page_num=12, page=page)

     content = result[0]

     page = result[1]

     paginator_range = getPaginatorRange(page)

     templateParams = {
         'url_paginator': url_paginator,
         'content': content,
         'page': page,
         'paginator_range': paginator_range

     }

     template = loader.get_template('Products/contentPage.html')
     context = RequestContext(request, templateParams)
     rendered = template.render(context)

     return rendered













def _getdetailcontent(request, item_id, slug):
     product = get_object_or_404(Product, pk=item_id)

     attr = (
        'NAME', 'COST', 'CURRENCY', 'IMAGE', 'DETAIL_TEXT',
        'COUPON_DISCOUNT', 'DISCOUNT', 'MEASUREMENT_UNIT',
        'DOCUMENT_1', 'DOCUMENT_2', 'DOCUMENT_3', 'SKU'
     )

     productValues = product.getAttributeValues(*attr)



     photos = Gallery.objects.filter(c2p__parent=item_id)

     additionalPages = AdditionalPages.objects.filter(c2p__parent=item_id)

     country = Country.objects.get(p2c__child__p2c__child=item_id, p2c__type="dependence", p2c__child__p2c__type="dependence")

     company = Company.objects.get(p2c__child=item_id)
     companyValues = company.getAttributeValues("NAME", 'ADDRESS', 'FAX', 'TELEPHONE_NUMBER', 'SITE_NAME', 'SLUG')
     companyValues.update({'COMPANY_ID': company.id})


     countriesList = country.getAttributeValues("NAME", 'FLAG', 'COUNTRY_FLAG')

     toUpdate = {
        'COUNTRY_NAME': countriesList.get('NAME', 0),
        'COUNTRY_FLAG': countriesList.get('FLAG', 0),
        'FLAG_CLASS': countriesList.get('COUNTRY_FLAG', 0),
        'COUNTRY_ID':  country.id
     }

     companyValues.update(toUpdate)

     template = loader.get_template('Products/detailContent.html')

     templateParams = {
        'productValues': productValues,
        'photos': photos,
        'additionalPages': additionalPages,
        'companyValues': companyValues,
        'item_id': item_id
     }

     context = RequestContext(request, templateParams)
     rendered = template.render(context)




     return rendered














