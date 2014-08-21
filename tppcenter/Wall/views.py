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

    filters, searchFilter = func.filterLive(request, model_name='Wall')

    innov_projects = func.getActiveSQS().models(InnovationProject)
    products = func.getActiveSQS().models(Product)
    proposals = func.getActiveSQS().models(BusinessProposal)
    exhibitions = func.getActiveSQS().models(Exhibition)



    if len(searchFilter) > 0:
        innov_projects = innov_projects.filter(searchFilter)
        products = products.filter(searchFilter)
        proposals = proposals.filter(searchFilter)
        exhibitions = exhibitions.filter(searchFilter)

    q = request.GET.get('q', '')

    if q != '':
        innov_projects = innov_projects.filter(title=q)
        products = products.filter(title=q)
        proposals = proposals.filter(title=q)
        exhibitions = exhibitions.filter(title=q)

    sortFields = {
          'date': 'obj_create_date',
          'name': 'title_sort'
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
        order.append('-obj_create_date')



    innov_projects = innov_projects.order_by(*order)[:1]
    products = products.order_by(*order)[:4]
    proposals = proposals.order_by(*order)[:1]
    exhibitions = exhibitions.order_by(*order)[:1]

    #------------------Innov--------------------------#
    #innov_projects = func.getActiveSQS().models(InnovationProject).order_by("-obj_create_date")[:1]
    innov_ids = [project.pk for project in innov_projects]
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

    products_ids = [product.pk for product in products]
    productsValues = Item.getItemsAttributesValues(('NAME', 'IMAGE', 'COST', 'CURRENCY', 'SLUG'), products_ids)
    func.addDictinoryWithCountryAndOrganization(products_ids, productsValues)

    #---------------News---------------------------------#
    #PAY ATTENTION HARDCODED CATEGORY
    exlude_category = 85347
    news = func.getActiveSQS().models(News).filter(categories__gt=0).exclude(categories=exlude_category).order_by("-obj_create_date")[:1]
    news_ids = [new.pk for new in news]
    newsValues = Item.getItemsAttributesValues(('NAME', 'IMAGE', 'DETAIL_TEXT', 'SLUG'), news_ids)
    func.addDictinoryWithCountryAndOrganization(news_ids, newsValues)


    #---------------BusinessProposal--------------------#

    proposals_ids = [proposal.pk for proposal in proposals]
    proposalsValues = Item.getItemsAttributesValues(('NAME', 'SLUG'), proposals_ids)
    func.addDictinoryWithCountryAndOrganization(proposals_ids, proposalsValues)


    #--------------Exhibitions--------------------------#

    exhibitions_ids = [exhibition.pk for exhibition in exhibitions]
    exhibitionsValues = Item.getItemsAttributesValues(('NAME', 'CITY', 'COUNTRY', 'START_EVENT_DATE',
                                                       'END_EVENT_DATE', 'SLUG'), exhibitions_ids)
    func.addDictinoryWithCountryAndOrganization(exhibitions_ids, exhibitionsValues)


    template = loader.get_template('Wall/contentPage.html')

    templateParams = {
       'filters': filters,
       'sortField1': sortField1,
       'sortField2': sortField2,
       'order1': order1,
       'order2': order2,
       'newsValues': newsValues,
       'exhibitionsValues': exhibitionsValues,
       'productsValues': productsValues,
       'innovValues': innovValues,
       'proposalsValues': proposalsValues
    }

    context = RequestContext(request, templateParams)

    return template.render(context)




