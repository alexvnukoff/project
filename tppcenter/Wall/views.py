from django.conf import settings
from django.contrib.sites.models import Site
from django.http import HttpResponse
from haystack.query import SearchQuerySet
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
    products = products.exclude(sites=Site.objects.get(name="centerpokupok").pk).order_by(*order)[:4]
    proposals = proposals.order_by(*order)[:1]
    exhibitions = exhibitions.order_by(*order)[:1]

    #------------------Innov--------------------------#
    #innov_projects = func.getActiveSQS().models(InnovationProject).order_by("-obj_create_date")[:1]

    branches_ids = []

    for proj in innov_projects:
        branches_ids += proj.branch

    branchesList = SearchQuerySet().models(Branch).filter(django_id__in=branches_ids)

    branches_dict = {}

    for branch in branchesList:
        branches_dict[branch.pk] = branch

    innovValues = []

    for proj in innov_projects:

        branches = []

        for branch in proj.branch:
            if branch in branches_dict:
                branches.append(branches_dict[branch])

        proj.branch = branches
        innovValues.append(proj)

    innovValues = func.get_countrys_for_sqs_objects(innovValues)
    innovValues = func.get_organization_for_objects(innovValues)
    innovValues = func.get_cabinet_data_for_objects(innovValues)

    #----------------Product----------------------------#

    productsValues = func.get_countrys_for_sqs_objects(products)
    productsValues = func.get_organization_for_objects(productsValues)

    #---------------News---------------------------------#
    #TODO:PAY ATTENTION HARDCODED CATEGORY
    exlude_category = 85347
    news = func.getActiveSQS().models(News).exclude(categories=exlude_category).order_by("-obj_create_date")[:1]
    newsValues = func.get_countrys_for_sqs_objects(news)
    newsValues = func.get_organization_for_objects(newsValues)


    #---------------BusinessProposal--------------------#

    proposalsValues = func.get_countrys_for_sqs_objects(proposals)
    proposalsValues = func.get_organization_for_objects(proposalsValues)


    #--------------Exhibitions--------------------------#

    exhibitionsValues = func.get_organization_for_objects(exhibitions)
    exhibitionsValues = func.get_countrys_for_sqs_objects(exhibitionsValues)


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




