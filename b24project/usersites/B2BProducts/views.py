# -*- encoding: utf-8 -*-

import json 
import logging

from collections import OrderedDict

from django.utils.translation import ugettext as _
from django.http import HttpResponse

from b24online.models import B2BProduct, B2BProductCategory
from tpp.DynamicSiteMiddleware import get_current_site
from usersites.cbv import ItemDetail, ItemList
from usersites.mixins import UserTemplateMixin

logger = logging.getLogger(__name__)


class B2BProductList(UserTemplateMixin, ItemList):
    model = B2BProduct
    template_name = '{template_path}/B2BProducts/contentPage.html'
    paginate_by = 16
    filter_key = 'company'
    url_paginator = "b2b_products:paginator"
    current_section = _("B2B Products")
    title = _("B2B Products")

    def dispatch(self, request, *args, **kwargs):
        category_pk = kwargs.pop('pk', None)

        if category_pk:
            self.category = B2BProductCategory.objects.get(pk=category_pk)
        else:
            self.category = None

        return super().dispatch(request, *args, **kwargs)

    def _load_category_hierarchy(self, categories, loaded_categories=None):

        if not loaded_categories:
            loaded_categories = {}

        categories_to_load = []

        for category in categories:
            loaded_categories[category.pk] = category

            if category.parent_id and category.parent_id not in loaded_categories:
                categories_to_load.append(category.parent_id)

        if categories_to_load:
            queryset = B2BProductCategory.objects.filter(pk__in=categories_to_load).order_by('level')
            loaded_categories = self._load_category_hierarchy(queryset, loaded_categories)

        return loaded_categories

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        organization = get_current_site().user_site.organization
        categories = B2BProductCategory.objects.filter(products__company_id=organization.pk)\
            .order_by('level').distinct()

        context_data['categories'] = OrderedDict(sorted(
            self._load_category_hierarchy(categories).items(), key=lambda x: [x[1].tree_id, x[1].lft]))

        context_data['selected_category'] = self.category

        return context_data

    def get_url_paginator(self):
        if self.category:
            return "b2b_products:category_paged"

        return self.url_paginator

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.category:
            if self.category.is_leaf_node():
                categories = [self.category]
            else:
                categories = self.category.get_descendants(include_self=True)

            queryset = queryset.filter(categories__in=categories).distinct()

        return queryset


class B2BProductListDetail(UserTemplateMixin, ItemDetail):
    model = B2BProduct
    filter_key = 'company'
    template_name = '{template_path}/B2BProducts/detailContent.html'


def get_b2bproduct_json(request):
    """
    Return the B2BProduct data json.
    """
    from b24online.search_indexes import B2BProductIndex, SearchEngine

    term = request.GET.get('term')
    if term and len(term) > 2:
        se_qs = SearchEngine(B2BProductIndex).query('match', name_auto=term)
        qs = B2BProduct.objects.filter(
            id__in=(item.django_id for item in se_qs),
            is_active=True
        ).order_by('name')
    else:
        qs = B2BProduct.objects.none()
    data = [{'id': item.id, 'value': item.name, 'img': item.image.small} \
        for item in qs]
    return HttpResponse(json.dumps(data), content_type='application/json')
