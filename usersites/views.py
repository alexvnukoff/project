from haystack.backends import SQ
from appl.func import getActiveSQS
from appl.models import Product,  UserSites, News, BusinessProposal, AdditionalPages, Organization
from core.models import Item
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _
from django.conf import settings


def get_wall(request, page_id=None, language=None, about=None):

    if page_id is not None:
        page = get_object_or_404(AdditionalPages, pk=page_id)
        contentPage = getAdditionalPage(request, page)
        current_section = ""
        title = ""
    else:
        contentPage = _get_content(request, language)
        current_section = _("Wall")
        title = _("Wall")
    if about:
        contentPage = getAboutUsPage(request)
        current_section = _("About us")
        title = _("About us")




    templateParams = {
    'current_section': current_section,
    'contentPage': contentPage,
    'title': title
    }

    return render_to_response("index.html", templateParams, context_instance=RequestContext(request))

def _get_content(request, language):
     user_site = UserSites.objects.get(sites__id=settings.SITE_ID)
     organization = user_site.organization.pk

     sqs = getActiveSQS().models(News).filter(SQ(tpp=organization) |
                                              SQ(company=organization)).order_by('-obj_create_date')[:3]
     news_ids = [new.pk for new in sqs]

     attr = ('NAME', 'ANONS', 'DETAIL_TEXT', 'SLUG', 'IMAGE')

     newsValues = Item.getItemsAttributesValues(attr, news_ids)



     sqs = getActiveSQS().models(BusinessProposal).filter(SQ(tpp=organization) |
                                              SQ(company=organization)).order_by('-obj_create_date')[:3]
     proposals_ids = [proposal.pk for proposal in sqs]

     attr = ('NAME', 'ANONS', 'DETAIL_TEXT', 'SLUG')

     proposalValues = Item.getItemsAttributesValues(attr, proposals_ids)



     sqs = getActiveSQS().models(Product).filter(SQ(tpp=organization) |
                                              SQ(company=organization)).order_by('-obj_create_date')[:4]
     product_ids = [product.pk for product in sqs]

     attr = ('NAME', 'COST', 'CURRENCY', 'SLUG', 'IMAGE')

     productValues = Item.getItemsAttributesValues(attr, product_ids)

     if language:
         news_url = "news_lang:detail"
         proposal_url = 'proposal_lang:detail'
         products_url = 'products_lang:detail'
     else:
         news_url = "news:detail"
         proposal_url = 'proposal:detail'
         products_url = 'products:detail'







     templateParams = {
         'newsValues': newsValues,
         'proposalValues': proposalValues,
         'productValues': productValues,
         'url_parameter': language if language else [],
         'news_url': news_url,
         'products_url': products_url,
         'proposal_url': proposal_url



     }

     template = loader.get_template('contentPage.html')
     context = RequestContext(request, templateParams)
     rendered = template.render(context)

     return rendered



def getAdditionalPage(request, page):

    pageValues = page.getAttributeValues('NAME', 'DETAIL_TEXT')

    templateParams = {'pageValues': pageValues, }

    template = loader.get_template('additional_page.html')
    context = RequestContext(request, templateParams)
    rendered = template.render(context)

    return rendered


def getAboutUsPage(request):
     user_site = UserSites.objects.get(sites__id=settings.SITE_ID)
     organization = user_site.organization

     content = organization.getAttributeValues('DETAIL_TEXT')

     templateParams = {'content': content }

     template = loader.get_template('about_us.html')
     context = RequestContext(request, templateParams)
     rendered = template.render(context)

     return rendered










