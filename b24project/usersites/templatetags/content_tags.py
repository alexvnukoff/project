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


@register.inclusion_tag('usersites_templates/dummy_extends_template.html', takes_context=True)
def b2c_products(context, template_name, on_page, page=1, selected_category=None, search_query=None):
    if search_query is None:
        url_paginator = "b2c_products:category_paged" if selected_category else "b2c_products:paginator"
    else:
        url_paginator = "b2c_products:search_paginator"

    extended_context = copy(context)
    categories = None
    category = None

    if selected_category:
        category = B2CProductCategory.objects.get(pk=selected_category)
        extended_context['url_parameter'] = [category.slug, category.pk]

        if category.is_leaf_node():
            categories = [category]
        else:
            categories = category.get_descendants(include_self=True)

    search_query = search_query.strip() if search_query else None

    if search_query:
        s = SearchEngine(doc_type=B2CProduct.get_index_model())
        s = s.query('match', name=search_query)\
            .query('match', is_active=True)\
            .query('match', is_deleted=False)\
            .query('match', organization=get_current_site().user_site.organization.pk)
        
        if categories:
            s = s.filter('terms', b2c_categories=list(b2c_categories.values_list('pk', flat=True)))
        
        s = s.sort('name')
        
        paginator = Paginator(s, on_page, allow_empty_first_page=True)
        page = paginator.page(page or 1)
        paginator, page, search_results, is_paginated = (paginator, page, page.object_list, page.has_other_pages())
        object_ids = [hit.django_id for hit in search_results]
        queryset = B2CProduct.objects.filter(pk__in=object_ids).order_by('name')
    else:
        filter_kwargs = {'company': get_current_site().user_site.organization}
        
        if categories:
            filter_kwargs['categories__in'] = categories

        queryset = B2CProduct.get_active_objects().filter(**filter_kwargs).order_by('name')
        
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
