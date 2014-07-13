from haystack.backends import SQ
from appl import func
from appl.func import getActiveSQS, setPaginationForSearchWithValues, getPaginatorRange
from appl.models import BusinessProposal,  UserSites, Gallery, AdditionalPages
from core.models import Item
from django.core.exceptions import ObjectDoesNotExist
from django.http import  HttpResponse, HttpResponseNotFound
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _
from django.conf import settings

def get_proposals_list(request, page=1, item_id=None, my=None, slug=None, language=None):


    if item_id:
       if not Item.active.get_active().filter(pk=item_id).exists():
         return HttpResponseNotFound()




    try:
        if not item_id:

            contentPage = _get_content(request, page, language)

        else:
            contentPage = _getdetailcontent(request, item_id, slug)
            if isinstance(contentPage, HttpResponse):
                return contentPage



    except ObjectDoesNotExist:
        contentPage = func.emptyCompany()





    current_section = _("Business proposals")
    title = _("Business proposals")

    templateParams = {
    'current_section': current_section,
    'contentPage': contentPage,
    'title': title
    }

    return render_to_response("index.html", templateParams, context_instance=RequestContext(request))








def _get_content(request, page, language):
     user_site = UserSites.objects.get(sites__id=settings.SITE_ID)
     organization = user_site.organization.pk

     sqs = getActiveSQS().models(BusinessProposal).filter(SQ(tpp=organization) |
                                              SQ(company=organization)).order_by('-obj_create_date')

     if not language:
         url_paginator = 'proposal:paginator'
         proposal_url = 'proposal:detail'
     else:
         url_paginator ="proposal_lang:paginator"
         proposal_url = 'proposal_lang:detail'



     attr = ('NAME',  'DETAIL_TEXT', 'SLUG', 'ANONS')

     result = setPaginationForSearchWithValues(sqs, *attr, page_num=10, page=page)

     content = result[0]

     page = result[1]

     paginator_range = getPaginatorRange(page)

     templateParams = {
         'url_parameter': language if language else [],
         'url_paginator': url_paginator,
         'content': content,
         'page': page,
         'paginator_range': paginator_range,
         'proposal_url': proposal_url

     }

     template = loader.get_template('Proposals/contentPage.html')
     context = RequestContext(request, templateParams)
     rendered = template.render(context)

     return rendered













def _getdetailcontent(request, item_id, slug):
     proposal = get_object_or_404(BusinessProposal, pk=item_id)
     proposalValues = proposal.getAttributeValues(*('NAME', 'DETAIL_TEXT', 'DOCUMENT_1', 'DOCUMENT_2', 'DOCUMENT_3', 'SLUG'))
     description = proposalValues.get('DETAIL_TEXT', False)[0] if proposalValues.get('DETAIL_TEXT', False) else ""
     description = func.cleanFromHtml(description)
     title = proposalValues.get('NAME', False)[0] if proposalValues.get('NAME', False) else ""

     photos = Gallery.objects.filter(c2p__parent=item_id)

     additionalPages = AdditionalPages.objects.filter(c2p__parent=item_id)

     func.addToItemDictinoryWithCountryAndOrganization(proposal.id, proposalValues, withContacts=True)

     template = loader.get_template('Proposals/detailContent.html')

     templateParams = {
        'proposalValues': proposalValues,
        'photos': photos,
        'additionalPages': additionalPages,
        'item_id': item_id
     }

     context = RequestContext(request, templateParams)
     rendered = template.render(context)


     return rendered














