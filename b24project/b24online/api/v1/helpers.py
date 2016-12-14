from django.core.paginator import Paginator
from django.utils.functional import cached_property

from b24online.models import Country
from b24online.search_indexes import SearchEngine


class ContentHelper:
    valid_filters = {}

    def __init__(self, request, page_size, queryset, page=1):
        self.request = request
        self.page_size = page_size
        self.queryset = queryset

    @property
    def page(self):
        page = 1

        try:
            page = int(self.request.query_params.get('page', 1))
        except ValueError:
            pass

        return page

    @property
    def applied_filters(self):
        applied_filters = {}

        for f, model in self.valid_filters.items():
            values = self._filter_values(f)

            if values:
                applied_filters[f] = model.objects.filter(pk__in=values).only('pk', 'name')

        # Apply geo_country by our internal code
        if self.request.session.get('geo_country') and not self.request.query_params.get('order1'):
            geo_country = self.request.session['geo_country']
            applied_filters['country'] = Country.objects.filter(pk=geo_country).only('pk', 'name')

        return applied_filters

    @cached_property
    def search_query(self):
        return self.request.query_params.get('q', '').strip()

    def is_filtered(self):
        return self.applied_filters or self.search_query

    def get_filtered_queryset(self):
        if self.is_filtered():
            hits = self._apply_filters(self.queryset.model).sort(*self.sorting).execute().hits

            if hits.total > 0:
                return hits
            else:
                return self.queryset.none()

        return self.queryset.order_by(*self.sorting)

    @cached_property
    def paginator(self):
        return Paginator(self.get_filtered_queryset(), self.page_size)


    @property
    def content(self):
        page = self.paginator.page(self.page)

        if self.is_filtered():
            return self.queryset.filter(pk__in=[hit.django_id for hit in page.object_list])

        return page.object_list

    @property
    def sorting(self):
        return ('-created_at',)

    def _apply_filters(self, model):
        s = SearchEngine(doc_type=model.get_index_model())

        for filter_key in self.valid_filters:
            values = self._filter_values(filter_key)

            if values:
                s = s.filter('terms', **{filter_key: values})

        # Apply geo_country by our internal code
        if self.request.session.get('geo_country') and not self.request.query_params.get('order1'):
            s = s.filter('terms', **{'country': [self.request.session['geo_country']]})

        if self.search_query:
            s = s.query("multi_match", query=self.search_query, fields=['title', 'name', 'description', 'content'])

        return s.query('match', is_active=True).query('match', is_deleted=False)

    def _filter_values(self, filter_name):
        key = "filter[%s][]" % filter_name

        return self.request.query_params.getlist(key)

# class WallContentHelper(ContentHelper):
#     valid_filters = {
#         'country': Country,
#         'chamber': Chamber,
#         'branches': Branch
#     }
#
#     @property
#     def projects_queryset(self):
#         return InnovationProject.get_active_objects() \
#             .prefetch_related('organization', 'organization__countries')
#
#     @property
#     def products_queryset(self):
#         return B2BProduct.get_active_objects().select_related('country')
#
#     @property
#     def proposals_queryset(self):
#         return BusinessProposal.get_active_objects() \
#             .prefetch_related('branches', 'organization', 'organization__countries')
#
#     @property
#     def exhibitions_queryset(self):
#         return Exhibition.get_active_objects().select_related('country').prefetch_related('organization')
#
#     @property
#     def news_queryset(self):
#         return News.get_active_objects() \
#             .select_related('country').prefetch_related('organization', 'organization__countries')
#
#     @property
#     def data(self):
#         return {
#             'projects': self._content(self.projects_queryset, 1),
#             'products': self._content(self.products_queryset, 4),
#             'proposals': self._content(self.proposals_queryset, 1),
#             'exhibitions': self._content(self.exhibitions_queryset, 1),
#             'news': self._content(self.news_queryset, 1),
#         }

#
# class NewsContentHelper(ContentHelper):
#     @property
#     def news_queryset(self):
#         return News.get_active_objects() \
#             .select_related('country').prefetch_related('organization', 'organization__countries')
#
#     @property
#     def data(self):
#         return self._content(self.news_queryset, 10)
#
# class NewsContentHelper(ContentHelper):
#     @property
#     def news_queryset(self):
#         return News.get_active_objects() \
#             .select_related('country').prefetch_related('organization', 'organization__countries')
#
#     @property
#     def data(self):
#         return self._content(self.news_queryset, 10)
#
# class NewsContentHelper(ContentHelper):
#     @property
#     def news_queryset(self):
#         return News.get_active_objects() \
#             .select_related('country').prefetch_related('organization', 'organization__countries')
#
#     @property
#     def data(self):
#         return self._content(self.news_queryset, 10)
#
# class NewsContentHelper(ContentHelper):
#     @property
#     def news_queryset(self):
#         return News.get_active_objects() \
#             .select_related('country').prefetch_related('organization', 'organization__countries')
#
#     @property
#     def data(self):
#         return self._content(self.news_queryset, 10)
#
# class NewsContentHelper(ContentHelper):
#     @property
#     def news_queryset(self):
#         return News.get_active_objects() \
#             .select_related('country').prefetch_related('organization', 'organization__countries')
#
#     @property
#     def data(self):
#         return self._content(self.news_queryset, 10)
