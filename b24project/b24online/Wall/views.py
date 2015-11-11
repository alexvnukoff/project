import json

from django.conf import settings
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _

from b24online.models import InnovationProject, B2BProduct, BusinessProposal, Exhibition, News, Branch, Chamber, Country
from b24online.search_indexes import SearchEngine


def get_wall_list(request):
    current_section = _("Wall")

    wallPage = _wall_content(request)

    styles = [
        settings.STATIC_URL + 'b24online/css/news.css',
        settings.STATIC_URL + 'b24online/css/company.css'
    ]

    scripts = []

    if not request.is_ajax():
        templateParams = {
            'current_section': current_section,
            'wallPage': wallPage
        }

        return render_to_response("b24online/Wall/index.html", templateParams, context_instance=RequestContext(request))
    else:
        serialize = {
            'styles': styles,
            'scripts': scripts,
            'content': wallPage,

        }

        return HttpResponse(json.dumps(serialize))


def _wall_content(request):
    valid_filters = {
        'country': Country,
        'chamber': Chamber,
        'branches': Branch
    }

    q = request.GET.get('q', '').strip()
    applied_filters = {}

    for f, model in valid_filters.items():
        key = "filter[%s][]" % f
        values = request.GET.getlist(key)

        if values:
            applied_filters[f] = model.objects.filter(pk__in=values).only('pk', 'name')

    innovation_project = InnovationProject.get_active_objects()
    products = B2BProduct.get_active_objects().prefetch_related('company__countries')
    proposal = BusinessProposal.get_active_objects()
    exhibition = Exhibition.get_active_objects()
    # TODO, show only specific news
    news = News.get_active_objects()

    if applied_filters or q:
        filter_list = list(valid_filters.keys())
        #####################
        sort = get_sorting(request)
        hits = apply_filters(request, InnovationProject, q, filter_list).sort(*sort)[:1].execute().hits

        if hits.total > 0:
            innovation_project = innovation_project.get(pk=hits[0].django_id)
        else:
            innovation_project = None

        #####################
        sort = get_sorting(request)
        hits = apply_filters(request, B2BProduct, q, filter_list).sort(*sort)[:4].execute().hits
        obj_ids = [hit.django_id for hit in hits]
        products = products.filter(pk__in=obj_ids)

        #####################
        sort = get_sorting(request, {'date': 'created_at', 'name': 'title'})
        hits = apply_filters(request, BusinessProposal, q, filter_list).sort(*sort)[:1].execute().hits

        if hits.total > 0:
            proposal = proposal.get(pk=hits[0].django_id)
        else:
            proposal = None

        #####################
        sort = get_sorting(request, {'date': 'created_at', 'name': 'title'})
        hits = apply_filters(request, Exhibition, q, filter_list).sort(*sort)[:1].execute().hits

        if hits.total > 0:
            exhibition = exhibition.get(pk=hits[0].django_id)
        else:
            exhibition = None

        #####################
        sort = get_sorting(request, {'date': 'created_at', 'name': 'title'})
        hits = apply_filters(request, News, q, filter_list).sort(*sort)[:1].execute().hits

        if hits.total > 0:
            news = news.get(pk=hits[0].django_id)
        else:
            news = None
    else:
        sort = get_sorting(request)
        innovation_project = innovation_project.order_by(*sort).first()
        sort = get_sorting(request)
        products = products.order_by(*sort)[:4]
        sort = get_sorting(request, {'date': 'created_at', 'name': 'title'})
        proposal = proposal.order_by(*sort).first()
        sort = get_sorting(request, {'date': 'created_at', 'name': 'title'})
        exhibition = exhibition.order_by(*sort).first()
        sort = get_sorting(request, {'date': 'created_at', 'name': 'title'})
        news = news.order_by(*sort).first()

    template = loader.get_template('b24online/Wall/contentPage.html')

    template_params = {
        'applied_filters': applied_filters,
        'sortField1': request.GET.get('sortField1', 'date'),
        'sortField2': request.GET.get('sortField1', None),
        'order1': request.GET.get('sortField1', 'desc'),
        'order2': request.GET.get('sortField1', None),
        'news': news,
        'exhibition': exhibition,
        'products': products,
        'innovation_project': innovation_project,
        'proposal': proposal,
        'available_filters': list(valid_filters.keys())
    }

    context = RequestContext(request, template_params)

    return template.render(context)


def apply_filters(request, model, q, valid_filters):
    s = SearchEngine(doc_type=model.get_index_model())

    for filter_key in valid_filters:
        filter_lookup = "filter[%s][]" % filter_key
        values = request.GET.getlist(filter_lookup)

        if values:
            s = s.filter('terms', **{filter_key: values})

    if q:
        s = s.query("multi_match", query=q, fields=['title', 'name', 'description', 'content'])

    return s.query('match', is_active=True).query('match', is_deleted=False)


def get_sorting(request, sort_fields=None):
    if sort_fields is None:
        sort_fields = {
            'date': 'created_at',
            'name': 'name'
        }

    order = []

    sort_field1 = request.GET.get('sortField1', 'date')
    sort_field2 = request.GET.get('sortField2', None)
    order1 = request.GET.get('order1', 'desc')
    order2 = request.GET.get('order2', None)

    if sort_field1 and sort_field1 in sort_fields:
        if order1 == 'desc':
            order.append('-' + sort_fields[sort_field1])
        else:
            order.append(sort_fields[sort_field1])
    else:
        order.append(sort_fields['date'])

    if sort_field2 and sort_field1 in sort_fields:
        if order2 == 'desc':
            order.append('-' + sort_fields[sort_field2])
        else:
            order.append(sort_fields[sort_field2])

    return order
