from django.core.paginator import Paginator
from django.utils.functional import cached_property
from rest_framework.filters import BaseFilterBackend
from rest_framework.generics import ListAPIView
from rest_framework.pagination import BasePagination
from rest_framework.response import Response
from rest_framework.views import APIView

from b24online.models import Country, Chamber, B2BProductCategory, Branch, BusinessProposalCategory
from b24online.search_indexes import SearchEngine
from centerpokupok.models import B2CProductCategory


class ActiveObjectFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view=None, **kwargs):
        return queryset.query('match', is_active=True).query('match', is_deleted=False)


class UiFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view=None, **kwargs):

        for filter_key in view.valid_filters.keys():
            values = request.query_params.get(filter_key, '').strip()

            if values:
                queryset = queryset.filter('terms', **{filter_key: list(map(int, values.split(',')))})

        return queryset


class DefaultCountryFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view=None, **kwargs):
        # Apply geo_country by our internal code
        if request.session.get('geo_country', None):
            geo_country = request.session['geo_country']

            return queryset.filter('terms', country=[geo_country])

        return queryset


class UiSearchFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view=None, **kwargs):
        search_query = view.search_query

        if search_query:
            return queryset.query("multi_match", query=search_query, fields=['title', 'name', 'description', 'content'])

        return queryset


class FilteredPaginator(BasePagination):
    def get_paginated_response(self, data):
        result = {
            'content': data,
            'count': self.page.paginator.count,
            'page_size': self.view.page_size
        }
        result.update(self.view.get_filter_data())

        return Response(result)

    def paginate_queryset(self, queryset, request, view=None):
        is_elastic_query = isinstance(queryset, SearchEngine)

        if is_elastic_query:
            queryset = queryset.execute().hits

        paginator = Paginator(queryset, view.page_size)

        page_number = 1

        try:
            page_number = int(request.query_params.get('page', 1))
            page_number = paginator.num_pages if paginator.num_pages < page_number else page_number
        except ValueError:
            pass

        page = paginator.page(page_number)

        self.page = page
        self.request = request
        self.view = view

        if is_elastic_query:
            return list(view.queryset.filter(pk__in=[hit.django_id for hit in page.object_list]).all())

        return list(self.page)


class FilterableViewMixin:
    valid_filters = {
        'organization': Chamber,
        'chamber': Chamber,
        'country': Country,
        'countries': Country,
        'b2b_categories': B2BProductCategory,
        'b2c_categories': B2CProductCategory,
        'branches': Branch,
        'bp_categories': BusinessProposalCategory,
    }

    is_filterable = True
    search_query_param = 'q'

    @cached_property
    def is_filtered(self):
        return not set(self.valid_filters.keys()).isdisjoint(self.request.query_params.keys())

    @cached_property
    def filters(self):
        filter_backends = []

        if self.is_filterable:
            filter_backends += [UiSearchFilter, ActiveObjectFilter]

            if self.is_filtered:
                filter_backends += [UiFilter]
            else:
                filter_backends += [DefaultCountryFilter]

        return filter_backends

    @cached_property
    def applied_filters(self):
        applied_filters = {}

        if self.is_filtered:
            for f, model in self.valid_filters.items():
                values = self.request.query_params.get(f, '').strip()

                if values:
                    applied_filters[f] = list(model.objects.filter(pk__in=values.split(',')).values('id', 'name'))
        elif self.request.session.get('geo_country', None):
            geo_country = self.request.session['geo_country']
            applied_filters['country'] = list(Country.objects.filter(pk=geo_country).values('id', 'name'))

        return applied_filters

    @cached_property
    def search_query(self):
        return self.request.query_params.get(self.search_query_param, '').strip()

    def get_filter_data(self):
        return {
            'filters': self.applied_filters,
            'search_query': self.search_query
        }


class BaseListApi(ListAPIView, FilterableViewMixin):
    pagination_class = FilteredPaginator
    sorting = '-created_at',
    page_size = 10

    def filter_queryset(self, queryset):
        for backend in self.filters:
            queryset = backend().filter_queryset(self.request, queryset, view=self)

        return queryset

    def get_queryset(self):
        if self.is_filterable:
            return SearchEngine(doc_type=self.queryset.model.get_index_model()).sort(*self.sorting)

        return self.queryset.order_by(*self.sorting)


class BaseAdvertisementView(APIView, FilterableViewMixin):
    @cached_property
    def list_adv_filter(self):
        list_filter = {}

        if not self.is_filtered and self.request.session.get('geo_country', None) is None:
            return list_filter

        if self.is_filtered:
            filerable_models = [Chamber, Country, Branch]

            for filter_key, model in self.valid_filters.items():
                if model not in filerable_models:
                    continue

                values = self.request.query_params.get(filter_key, '').strip()

                if values:
                    key = model.__name__
                    list_filter[key] = list_filter.get(key, []) + values.split(',')

                    if model is Chamber:
                        countries = list(
                            Country.objects.filter(organizations__pk__in=values).values_list('pk', flat=True))
                        key = Country.__name__
                        list_filter[key] = list_filter.get(key, []) + countries
        else:
            geo_country = self.request.session['geo_country']
            list_filter[Country.__name__] = [geo_country]

        return list_filter
