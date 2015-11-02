from collections import OrderedDict
from django.contrib.sites.shortcuts import get_current_site
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm

from centerpokupok.models import B2CProduct, B2CProductCategory
from usersites.cbv import ItemDetail, ItemList


class B2CProductList(ItemList):
    model = B2CProduct
    template_name = 'usersites/B2CProducts/contentPage.html'
    paginate_by = 16
    filter_key = 'company'
    url_paginator = "b2c_products:paginator"
    current_section = _("B2C Products")
    title = _("B2C Products")

    def dispatch(self, request, *args, **kwargs):
        category_pk = kwargs.pop('pk', None)

        if category_pk:
            self.category = B2CProductCategory.objects.get(pk=category_pk)
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
            queryset = B2CProductCategory.objects.filter(pk__in=categories_to_load).order_by('level')
            loaded_categories = self._load_category_hierarchy(queryset, loaded_categories)

        return loaded_categories

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        organization = get_current_site(self.request).user_site.organization
        categories = B2CProductCategory.objects.filter(products__company_id=organization.pk)\
            .order_by('level').distinct()

        context_data['categories'] = OrderedDict(sorted(
            self._load_category_hierarchy(categories).items(), key=lambda x: [x[1].tree_id, x[1].lft]))

        context_data['selected_category'] = self.category

        return context_data

    def get_url_paginator(self):
        if self.category:
            return "b2c_products:category_paged"

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


class B2CProductDetail(ItemDetail):
    model = B2CProduct
    filter_key = 'company'
    template_name = 'usersites/B2CProducts/detailContent.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        domain = get_current_site(self.request).domain

        if self.object.currency and self.object.cost and self.object.company.company_paypal_account:
            paypal_dict = {
                "business": self.object.company.company_paypal_account,
                "amount": self.object.cost,
                "notify_url": "http://%s%s" % (domain, reverse('paypal-ipn')),
                "return_url": self.request.build_absolute_uri(),
                "cancel_return": self.request.build_absolute_uri(),
                "item_number": self.object.pk,
                "item_name": self.object.name,
                "no_shipping": 0,
                "quantity": 1,
                "currency_code": self.object.currency
            }

            context_data['paypal_form'] = PayPalPaymentsForm(initial=paypal_dict)

        return context_data