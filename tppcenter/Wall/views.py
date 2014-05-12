from django.conf import settings
from django.http import HttpResponse
from appl import func
from appl.models import InnovationProject, Product, BusinessProposal, Exhibition, News, Branch, NewsCategories
from core.models import Item
from django.template import RequestContext, loader
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
import json

def get_wall_list(request):

    current_section = _("Wall")

    wallPage = _wallContent(request)

    styles = [
        settings.STATIC_URL + 'tppcenter/css/news.css',
        settings.STATIC_URL + 'tppcenter/css/company.css'
    ]

    scripts = []

    if not request.is_ajax():

        templateParams = {
            'current_section': current_section,
            'wallPage': wallPage
        }

        return render_to_response("Wall/index.html", templateParams, context_instance=RequestContext(request))
    else:
        serialize = {
            'styles': styles,
            'scripts': scripts,
            'content': wallPage,

        }

        return HttpResponse(json.dumps(serialize))


def _wallContent(request):
    #------------------Innov--------------------------#
    innov_projects = func.getActiveSQS().models(InnovationProject).order_by("-obj_create_date")[:3]
    innov_ids = [project.id for project in innov_projects]
    innovValues = Item.getItemsAttributesValues(('NAME', 'SLUG', 'COST', 'CURRENCY'), innov_ids)

    branches = Branch.objects.filter(p2c__child__in=innov_ids).values('p2c__child', 'pk')
    branches_ids = [branch['pk'] for branch in branches]
    branchesList = Item.getItemsAttributesValues(("NAME",), branches_ids)

    branches_dict = {}

    for branch in branches:
        branches_dict[branch['p2c__child']] = branch['pk']

    func.addDictinoryWithCountryAndOrganizationToInnov(innov_ids, innovValues)

    for id, innov in innovValues.items():

        toUpdate = {
            'BRANCH_NAME': branchesList[branches_dict[id]].get('NAME', 0) if branches_dict.get(id, 0) else [0],
            'BRANCH_ID': branches_dict.get(id, 0)
        }

        innov.update(toUpdate)


    #----------------Product----------------------------#
    products = func.getActiveSQS().models(Product).order_by("-obj_create_date")[:4]
    products_ids = [product.id for product in products]
    productsValues = Item.getItemsAttributesValues(('NAME', 'IMAGE', 'COST', 'CURRENCY', 'SLUG'), products_ids)
    func.addDictinoryWithCountryAndOrganization(products_ids, productsValues)

    #---------------News---------------------------------#
    #PAY ATTENTION HARDCODED CATEGORY
    exlude_category = 85347
    news = func.getActiveSQS().models(News).filter(categories__gt=0).exclude(categories=exlude_category).order_by("-obj_create_date")[:3]
    news_ids = [new.id for new in news]
    newsValues = Item.getItemsAttributesValues(('NAME', 'IMAGE', 'DETAIL_TEXT', 'SLUG'), news_ids)
    func.addDictinoryWithCountryAndOrganization(news_ids, newsValues)


    #---------------BusinessProposal--------------------#
    proposals = func.getActiveSQS().models(BusinessProposal).order_by("-obj_create_date")[:3]
    proposals_ids = [proposal.id for proposal in proposals]
    proposalsValues = Item.getItemsAttributesValues(('NAME', 'SLUG'), proposals_ids)
    func.addDictinoryWithCountryAndOrganization(proposals_ids, proposalsValues)


    #--------------Exhibitions--------------------------#
    exhibitions = func.getActiveSQS().models(Exhibition).order_by("-obj_create_date")[:3]
    exhibitions_ids = [exhibition.id for exhibition in exhibitions]
    exhibitionsValues = Item.getItemsAttributesValues(('NAME', 'CITY', 'COUNTRY', 'START_EVENT_DATE',
                                                       'END_EVENT_DATE', 'SLUG'), exhibitions_ids)
    func.addDictinoryWithCountryAndOrganization(exhibitions_ids, exhibitionsValues)


    template = loader.get_template('Wall/contentPage.html')

    templateParams = {
        'newsValues': newsValues,
        'exhibitionsValues': exhibitionsValues,
        'productsValues': productsValues,
        'innovValues': innovValues,
        'proposalsValues': proposalsValues
    }

    context = RequestContext(request, templateParams)

    return template.render(context)




