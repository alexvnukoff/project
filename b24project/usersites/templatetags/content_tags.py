from collections import OrderedDict
from copy import copy

from django import template
from django.core.paginator import Paginator
from django.utils.timezone import now

from appl import func
from b24online.models import B2BProduct, B2BProductCategory, News, BusinessProposal, Company, Producer, \
                             QuestionnaireCase
    
from b24online.search_indexes import SearchEngine
from b24online.utils import get_template_with_base_path, load_category_hierarchy
from centerpokupok.models import B2CProduct, B2CProductCategory
from tpp.DynamicSiteMiddleware import get_current_site

register = template.Library()


class ItemsTag:
    def __init__(self, context, queryset, template_path, on_page, current_page, url_paginator, queryset_key, order_by):
        self.context = context
        self.queryset = queryset
        self.queryset_key = queryset_key
        self.template_path = template_path
        self.on_page = on_page
        self.current_page = current_page or 1
        self.url_paginator = url_paginator
        self.order_by = order_by

    def get_queryset(self):
        return self.queryset.order_by(self.order_by)

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
    def __init__(self, selected_category, search_query=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category = self.get_category_model().objects.get(pk=selected_category) if selected_category else None
        self.selected_category = self.category
        self.search_query = search_query.strip() if search_query else None
        self.producer = self.context['request'].GET.get('pr', False)

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
            s = s.query('match', name=self.search_query) \
                .query('match', is_active=True) \
                .query('match', is_deleted=False) \
                .query('match', organization=get_current_site().user_site.organization.pk)

            if categories:
                s = s.filter('terms', b2c_categories=categories, b2b_categories=categories)

            return s.sort(self.order_by)
        else:
            if categories and self.producer:
                return self.queryset.filter(categories__in=categories, producer__pk=self.producer)

            if categories and not self.producer:
                return self.queryset.filter(categories__in=categories)

            if not categories and self.producer:
                return self.queryset.filter(producer__pk=self.producer)

            return self.queryset.order_by(self.order_by)

    @property
    def result_data(self):
        extended_context = super().result_data

        if self.selected_category:
            extended_context['selected_category'] = self.category

        if self.category:
            extended_context['url_parameter'] = [self.category.slug, self.category.pk]

        if self.producer:
            extended_context['selected_producer'] = self.producer

        if self.search_query:
            objects_on_page = [hit.django_id for hit in extended_context[self.queryset_key]]
            extended_context[self.queryset_key] = self.queryset.model.objects.filter(pk__in=objects_on_page)

        return extended_context


@register.inclusion_tag('usersites_templates/dummy_extends_template.html', takes_context=True)
def b2b_products(context, template_name, on_page, page=1, selected_category=None, search_query=None,
                 order_by='-created_at'):

    if search_query is None:
        url_paginator = "b2b_products:category_paged" if selected_category else "b2b_products:paginator"
    else:
        url_paginator = "b2b_products:search_paginator"

    organization = get_current_site().user_site.organization

    if isinstance(organization, Company):
        queryset = B2BProduct.get_active_objects().filter(company=organization)
    else:
        queryset = B2BProduct.objects.none()

    return ProductsTag(
        order_by=order_by,
        selected_category=selected_category,
        search_query=search_query,
        context=context,
        queryset=queryset,
        template_path=template_name,
        on_page=on_page,
        current_page=page,
        url_paginator=url_paginator,
        queryset_key='products').result_data


@register.inclusion_tag('usersites_templates/dummy_extends_template.html', takes_context=True)
def b2c_products(context, template_name, on_page, page=1, selected_category=None, search_query=None,
                 order_by='-created_at'):

    if search_query is None:
        url_paginator = "b2c_products:category_paged" if selected_category else "b2c_products:paginator"
    else:
        url_paginator = "b2c_products:search_paginator"

    organization = get_current_site().user_site.organization

    if isinstance(organization, Company):
        queryset = B2CProduct.get_active_objects().filter(company=organization)
    else:
        queryset = B2CProduct.objects.none()

    return ProductsTag(
        order_by=order_by,
        selected_category=selected_category,
        search_query=search_query,
        context=context,
        queryset=queryset,
        template_path=template_name,
        on_page=on_page,
        current_page=page,
        url_paginator=url_paginator,
        queryset_key='products').result_data


@register.inclusion_tag('usersites_templates/dummy_extends_template.html', takes_context=True)
def coupons(context, template_name, on_page, page=1, selected_category=None, order_by='-created_at'):
    # TODO
    url_paginator = None if selected_category else None
    organization = get_current_site().user_site.organization

    if isinstance(organization, Company):
        queryset = B2CProduct.get_active_objects().filter(company=organization,
                                                          coupon_dates__contains=now().date(),
                                                          coupon_discount_percent__gt=0)
    else:
        queryset = B2CProduct.objects.none()

    return ProductsTag(
        order_by=order_by,
        selected_category=selected_category,
        context=context,
        queryset=queryset,
        template_path=template_name,
        on_page=on_page,
        current_page=page,
        url_paginator=url_paginator,
        queryset_key='coupons').result_data


@register.inclusion_tag('usersites_templates/dummy_extends_template.html', takes_context=True)
def news(context, template_name, on_page, page=1, order_by='-created_at'):
    queryset = News.get_active_objects().filter(organization=get_current_site().user_site.organization)

    return ItemsTag(
        order_by=order_by,
        context=context,
        queryset=queryset,
        template_path=template_name,
        on_page=on_page,
        current_page=page,
        url_paginator='news:paginator',
        queryset_key='news').result_data


@register.inclusion_tag('usersites_templates/dummy_extends_template.html', takes_context=True)
def proposal(context, template_name, on_page, page=1, order_by='-created_at'):
    queryset = BusinessProposal.get_active_objects().filter(organization=get_current_site().user_site.organization)

    return ItemsTag(
        order_by=order_by,
        context=context,
        queryset=queryset,
        template_path=template_name,
        on_page=on_page,
        current_page=page,
        url_paginator='proposal:paginator',
        queryset_key='proposals').result_data


@register.inclusion_tag('usersites_templates/dummy_extends_template.html', takes_context=True)
def questionnaires_history(context, template_name, on_page, page=1, email=None, order_by='-created_at'):
    queryset = QuestionnaireCase.get_active_objects()\
        .filter(participants__email=email).distinct()

    return ItemsTag(
        order_by=order_by,
        context=context,
        queryset=queryset,
        template_path=template_name,
        on_page=on_page,
        current_page=page,
        url_paginator='questionnaires:case_list_paginator',
        queryset_key='cases').result_data


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


@register.simple_tag
def b2b_producers():
    organization = get_current_site().user_site.organization
    producers = B2BProduct.objects.filter(company_id=organization.pk).filter(
            producer__isnull=False).values_list('producer__pk', 'producer__name').distinct()
    return producers


@register.simple_tag
def b2c_producers():
    organization = get_current_site().user_site.organization
    producers = B2CProduct.objects.filter(company_id=organization.pk).filter(
            producer__isnull=False).values_list('producer__pk', 'producer__name').distinct()
    return producers


@register.filter
def check_pr_contain(producer_pk, uri):
    if '/?pr={0}'.format(producer_pk) in uri:
        return True
    return False

