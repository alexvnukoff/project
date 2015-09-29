from collections import OrderedDict

from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import ugettext as _

from b24online.models import B2BProduct, B2BProductCategory
from usersites.cbv import ItemDetail, ItemList


class B2BProductList(ItemList):
    model = B2BProduct
    template_name = 'B2BProducts/contentPage.html'
    paginate_by = 10
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
            queryset = B2BProduct.objects.filter(pk__in=categories_to_load).order_by('level')
            loaded_categories = self._load_category_hierarchy(queryset, loaded_categories)

        return loaded_categories

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        organization = get_current_site(self.request).user_site.organization
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

            queryset = queryset.filter(categories__in=categories)

        return queryset


class B2BProductListDetail(ItemDetail):
    model = B2BProduct
    filter_key = 'company'
    template_name = 'B2BProducts/detailContent.html'
