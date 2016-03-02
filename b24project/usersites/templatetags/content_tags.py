from collections import OrderedDict
from copy import copy
from django import template
from django.core.paginator import Paginator
from appl import func
from b24online.models import B2BProduct, B2BProductCategory
from b24online.search_indexes import SearchEngine
from b24online.utils import get_template_with_base_path, load_category_hierarchy
from centerpokupok.models import B2CProduct, B2CProductCategory
from tpp.DynamicSiteMiddleware import get_current_site

register = template.Library()


class ItemsTag:
    def __init__(self, context, queryset, template_path, on_page, current_page, url_paginator, queryset_key):
        self.context = context
        self.queryset = queryset
        self.queryset_key = queryset_key
        self.template_path = template_path
        self.on_page = on_page
        self.current_page = current_page or 1
        self.url_paginator = url_paginator

    def get_queryset(self):
        return self.queryset

    def get_paged_data(self):
        paginator = Paginator(self.get_queryset(), self.on_page, allow_empty_first_page=True)
        page = paginator.page(self.current_page)
        paginator, page, queryset, is_paginated = (paginator, page, page.object_list, page.has_other_pages())

        return {
            'page': page,
            'on_page': self.on_page,
            'paginator': paginator,
            'page_obj': page,
            'is_paginated': is_paginated,
            'paginator_range': func.get_paginator_range(page),
            self.queryset_key: queryset
        }

    @property
    def result_data(self):
        extended_context = copy(self.context)

        extended_context.update({
            'template': get_template_with_base_path(self.template_path),
            'url_paginator': self.url_paginator,
        })

        extended_context.update(self.get_paged_data())

        return extended_context


class ProductsTag(ItemsTag):
    def __init__(self, selected_category, search_query, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category = self.get_category_model().objects.get(pk=selected_category) if selected_category else None
        self.search_query = search_query.strip() if search_query else None

    def get_category_model(self):
        for field in self.queryset.model._meta.get_fields():
            if field.name == 'categories':
                return field.rel.to

        return None

    def get_queryset(self):
        categories = None

        if self.category:
            if self.category.is_leaf_node():
                categories = [self.category.pk]
            else:
                categories = list(self.category.get_descendants(include_self=True).values_list('pk', flat=True))

        if self.search_query:
            s = SearchEngine(doc_type=self.queryset.model.get_index_model())
            s.query('match', name=self.search_query) \
                .query('match', is_active=True) \
                .query('match', is_deleted=False) \
                .query('match', organization=get_current_site().user_site.organization.pk)

            if categories:
                s = s.filter('terms', b2c_categories=categories, b2b_categories=categories)

            return s.sort('name')
        else:
            if categories:
                return self.queryset.filter(categories__in=categories)

            return self.queryset

    @property
    def result_data(self):
        extended_context = super().result_data

        if self.category:
            extended_context['url_parameter'] = [self.category.slug, self.category.pk]

        if self.search_query:
            objects_on_page = [hit.django_id for hit in extended_context[self.queryset]]
            extended_context[self.queryset_key] = self.queryset.model.objects.filter(pk__in=objects_on_page)

        return extended_context


@register.inclusion_tag('usersites_templates/dummy_extends_template.html', takes_context=True)
def b2b_products(context, template_name, on_page, page=1, selected_category=None, search_query=None):
    if search_query is None:
        url_paginator = "b2b_products:category_paged" if selected_category else "b2b_products:paginator"
    else:
        url_paginator = "b2c_products:search_paginator"

    extended_context = copy(context)
    categories = None
    category = None

    if selected_category:
        category = B2BProductCategory.objects.get(pk=selected_category)
        extended_context['url_parameter'] = [category.slug, category.pk]

        if category.is_leaf_node():
            categories = [category]
        else:
            categories = category.get_descendants(include_self=True)

    search_query = search_query.strip() if search_query else None

    if search_query:
        s = SearchEngine(doc_type=B2BProduct.get_index_model())
        s.query('match', name=search_query) \
            .query('match', is_active=True) \
            .query('match', is_deleted=False) \
            .query('match', organization=get_current_site().user_site.organization.pk)

        if categories:
            s = s.filter('terms', b2c_categories=list(b2c_categories.values_list('pk', flat=True)))

        s.sort('name')

        paginator = Paginator(s, on_page, allow_empty_first_page=True)
        page = paginator.page(page or 1)
        paginator, page, search_results, is_paginated = (paginator, page, page.object_list, page.has_other_pages())
        object_ids = [hit.django_id for hit in search_results]
        queryset = B2BProduct.objects.filter(pk__in=object_ids).order_by('name')
    else:
        filter_kwargs = {'company': get_current_site().user_site.organization}

        if categories:
            filter_kwargs['categories__in'] = categories

        queryset = B2BProduct.get_active_objects().filter(**filter_kwargs).order_by('name')

        paginator = Paginator(queryset, on_page, allow_empty_first_page=True)
        page = paginator.page(page or 1)
        paginator, page, queryset, is_paginated = (paginator, page, page.object_list, page.has_other_pages())

    extended_context.update({
        'template': get_template_with_base_path(template_name),
        'url_paginator': url_paginator,
        'page': page,
        'on_page': on_page,
        'selected_category': category,
        'paginator_range': func.get_paginator_range(page),
        'paginator': paginator,
        'page_obj': page,
        'is_paginated': is_paginated,
        'products': queryset
    })

    return extended_context


register.inclusion_tag('usersites_templates/dummy_extends_template.html', takes_context=True)
def b2c_products(context, template_name, on_page, page=1, selected_category=None, search_query=None):
    if search_query is None:
        url_paginator = "b2c_products:category_paged" if selected_category else "b2c_products:paginator"
    else:
        url_paginator = "b2c_products:search_paginator"

    return ProductsTag(
        selected_category=selected_category,
        search_query=search_query,
        context=context,
        queryset=B2CProduct.get_active_objects().filter(company=get_current_site().user_site.organization).order_by('name'),
        template_path=template_name,
        on_page=on_page,
        current_page=page,
        url_paginator=url_paginator,
        queryset_key='products').result_data

@register.simple_tag
def b2b_categories():
    organization = get_current_site().user_site.organization
    categories = B2BProductCategory.objects.filter(products__company_id=organization.pk) \
        .order_by('level').distinct()

    return OrderedDict(sorted(
        load_category_hierarchy(B2BProductCategory, categories).items(), key=lambda x: [x[1].tree_id, x[1].lft]))


@register.simple_tag
def b2c_categories():
    organization = get_current_site().user_site.organization
    categories = B2CProductCategory.objects.filter(products__company_id=organization.pk) \
        .order_by('level').distinct()

    return OrderedDict(sorted(
        load_category_hierarchy(B2CProductCategory, categories).items(), key=lambda x: [x[1].tree_id, x[1].lft]))
