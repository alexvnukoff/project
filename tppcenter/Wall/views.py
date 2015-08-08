import json

from django.conf import settings
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _

from b24online.models import InnovationProject, B2BProduct, BusinessProposal, Exhibition, News


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
    # filters, searchFilter = func.filterLive(request, model_name='Wall')
    filters = {}
    # innovation_projects = func.getActiveSQS().models(InnovationProject)
    # products = func.getActiveSQS().models(Product)
    # proposals = func.getActiveSQS().models(BusinessProposal)
    # exhibitions = func.getActiveSQS().models(Exhibition)
    #
    # if len(searchFilter) > 0:
    #     innovation_projects = innovation_projects.filter(searchFilter)
    #     products = products.filter(searchFilter)
    #     proposals = proposals.filter(searchFilter)
    #     exhibitions = exhibitions.filter(searchFilter)
    #
    # q = request.GET.get('q', '')
    #
    # if q != '':
    #     innovation_projects = innovation_projects.filter(title=q)
    #     products = products.filter(title=q)
    #     proposals = proposals.filter(title=q)
    #     exhibitions = exhibitions.filter(title=q)

    sortFields = {
        'date': 'created_at',
        'name': 'name'
    }

    order = ['created_at']

    sortField1 = request.GET.get('sortField1', 'date')
    sortField2 = request.GET.get('sortField2', None)
    order1 = request.GET.get('order1', 'desc')
    order2 = request.GET.get('order2', None)
    #
    # if sortField1 and sortField1 in sortFields:
    #     if order1 == 'desc':
    #         order.append('-' + sortFields[sortField1])
    #     else:
    #         order.append(sortFields[sortField1])
    # else:
    #     order.append('created_at')

    innovation_project = InnovationProject.objects.prefetch_related('organization', 'organization__countries').latest(*order)
    products = B2BProduct.objects.prefetch_related('company__countries').order_by(*order)[:4]
    proposal = BusinessProposal.objects.prefetch_related('organization', 'organization__countries') \
        .latest(*order)
    exhibition = Exhibition.objects.select_related('country')\
        .prefetch_related('organization','organization__countries').latest(*order)
    news = News.objects.select_related('country').prefetch_related('organization', 'organization__countries') \
        .latest(*order)  # TODO, show only specific news

    template = loader.get_template('Wall/contentPage.html')

    template_params = {
        'filters': filters,
        'sortField1': sortField1,
        'sortField2': sortField2,
        'order1': order1,
        'order2': order2,
        'news': news,
        'exhibition': exhibition,
        'products': products,
        'innovation_project': innovation_project,
        'proposal': proposal
    }

    context = RequestContext(request, template_params)

    return template.render(context)
