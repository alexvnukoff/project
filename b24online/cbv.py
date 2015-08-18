from urllib.parse import urlparse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import Http404
from django.template import RequestContext
from django.template.loader import get_template
from django.utils.text import Truncator
from django.views.generic import DetailView
from elasticsearch_dsl import F

from appl import func
from b24online.models import Chamber, BusinessProposalCategory, Branch, B2BProductCategory
from b24online.models import Country
from b24online.search_indexes import SearchEngine
from core.cbv import HybridListView


class ItemsList(HybridListView):

    paginate_by = 10
    allow_empty = True

    # Sorting fields
    sortField1 = 'date'
    sortField2 = None
    order1 = 'desc'
    order2 = None

    # Queryset taken from db not indexes
    querysetDB = False

    # Current page
    page = 1

    # Add namespace
    addUrl = ''

    # Section name
    current_section = ''

    # Pagination url
    url_paginator = None
    url_my_paginator = None

    url_parameter = []

    # Lists of required scripts and styles for ajax request
    scripts = []
    styles = []

    # Fields to sort by
    sortFields = {
        'date': 'created_at',
        'name': 'name'
    }

    # Applied filters
    filters = {}

    # My tab selected
    my = False

    # Allowed filter list
    filter_list = {
        'chamber': Chamber,
        'country': Country,
        'b2b_category': B2BProductCategory,
        'branch': Branch,
        'bp_category': BusinessProposalCategory,
    }

    def is_filtered(self):
        q = self.request.GET.get('q', '').strip()
        return bool(self.filters or q)

    def get_filtered_items(self):
        s = SearchEngine(doc_type=self.model.get_index_model())
        q = self.request.GET.get('q', '').strip()

        for filter_key in list(self.filter_list.keys()):
            filter_lookup = "filter[%s]" % filter_key
            values = self.request.GET.getlist(filter_lookup)

            if values:
                if filter_key == 'country':
                    s.filter = F('terms', country=values) | F('terms', countries=values)
                else:
                    s = s.filter('terms', {filter_key: values})

        if q:
            s = s.query("multi_match", query=q, fields=['title', 'name', 'description', 'content'])

        return self.filter_search_object(s)

    def get_data(self, context):
        # For JSON response
        template = get_template(self.template_name)
        context = RequestContext(self.request, context)

        return {
            'styles': self.styles,
            'scripts': self.scripts,
            'content': template.render(context),
            'addNew': '' if not self.addUrl else reverse(self.addUrl),
        }

    def get_context_data(self, **kwargs):
        context = super(ItemsList, self).get_context_data(**kwargs)

        context.update({
            'filters': self.filters,
            'sortField1': self.sortField1,
            'sortField2': self.sortField2,
            'order1': self.order1,
            'order2': self.order2,
            'page': context['page_obj'],
            'paginator_range': func.get_paginator_range(context['page_obj']),
            'url_parameter': self.url_parameter,
            'url_paginator': self.url_my_paginator if self.is_my() else self.url_paginator,
            'items_perms': None,  # Deprecated
            'current_path': self.request.get_full_path(),
            'addNew': '' if not self.addUrl else reverse(self.addUrl),
            'current_section': self.current_section,
            'styles': self.styles,
            'scripts': self.scripts,
            'model': self.model.__name__
        })

        if isinstance(context['object_list'], SearchEngine):
            object_ids = [hit.django_id for hit in context['object_list'].execute().hits]
            context['object_list'] = self.optimize_queryset(self.model.objects.filter(pk__in=object_ids))

        return context

    def ajax(self, request, *args, **kwargs):
        pass

    def no_ajax(self, request, *args, **kwargs):
        pass

    def get(self, request, *args, **kwargs):
        for f, model in self.filter_list.items():
            key = "filter[%s][]" % f
            values = request.GET.getlist(key)

            if values:
                self.filters[f] = model.objects.filter(pk__in=values).values('pk', 'name')

        if request.is_ajax():
            self.ajax(request, *args, **kwargs)
        else:
            self.no_ajax(request, *args, **kwargs)

        return super(ItemsList, self).get(request, *args, **kwargs)

    def _get_sorting_params(self):
        order = []

        self.sortField1 = self.request.GET.get('sortField1', 'date')
        self.sortField2 = self.request.GET.get('sortField2', None)
        self.order1 = self.request.GET.get('order1', 'desc')
        self.order2 = self.request.GET.get('order2', None)

        if self.sortField1 and self.sortField1 in self.sortFields:
            if self.order1 == 'desc':
                order.append('-' + self.sortFields[self.sortField1])
            else:
                order.append(self.sortFields[self.sortField1])
        else:
            order.append(self.sortFields['date'])

        if self.sortField2 and self.sortField2 in self.sortFields:
            if self.order2 == 'desc':
                order.append('-' + self.sortFields[self.sortField2])
            else:
                order.append(self.sortFields[self.sortField2])

        return order

    @property
    def _current_organization(self):
        return self.request.session.get('current_company', None)

    def is_my(self):
        return self.request.user.is_authenticated() and not self.request.user.is_anonymous() and self.my

    def filter_search_object(self, s):
        return s

    def optimize_queryset(self, queryset):
        return queryset

    def get_queryset(self):
        if self.is_filtered() and not self.is_my():
            return self.get_filtered_items().sort(*self._get_sorting_params())

        return self.optimize_queryset(self.model.objects.filter(is_active=True).order_by(*self._get_sorting_params()))


class ItemDetail(DetailView):
    context_object_name = 'item'
    item_id = None

    # Add namespace
    addUrl = ''

    # Section name
    current_section = ''

    def get_queryset(self):
        return self.model.objects.filter(is_active=True)

    def get_object(self, queryset=None):
        self.item_id = self.kwargs.get('item_id', None)
        # TODO: get by slug?

        if self.item_id:
            try:
                return self.get_queryset().get(pk=self.item_id)
            except ObjectDoesNotExist:
                raise Http404()
        else:
            raise AttributeError("Generic detail view %s must be called with "
                                 "either an object pk or a slug."
                                 % self.__class__.__name__)

    def _get_item_meta(self):
        title = getattr(self.object, 'title', '') or getattr(self.object, 'name', '')
        image = settings.MEDIA_URL + 'original/' + self.object.image

        if image:
            getattr(self.object, 'logo', '') or getattr(self.object, 'image', '')

        url = urlparse(self.request.build_absolute_uri())

        return {
            'title': Truncator(title).chars("80", truncate='...'),
            'image': getattr(self.object, 'logo', '') or getattr(self.object, 'image', ''),
            'url': url.scheme + "://" + url.netloc + url.path,
            'text': getattr(self.object, 'description', "") or getattr(self.object, 'content', "")
        }
        pass

    def get_context_data(self, **kwargs):
        context = super(ItemDetail, self).get_context_data(**kwargs)

        context.update({
            'item_id': self.item_id,
            'addNew': '' if not self.addUrl else reverse(self.addUrl),
            'current_section': self.current_section,
            'meta': {}
        })

        return context
