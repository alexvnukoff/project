# -*- coding: utf-8 -*-
import re
from collections import OrderedDict

from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render
from django.template import loader
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.views.generic.edit import FormView
from paypal.standard.forms import PayPalPaymentsForm

from centerpokupok.Basket import Basket
from centerpokupok.forms import OrderEmailForm
from centerpokupok.models import B2CProduct, B2CProductCategory
from b24online.search_indexes import B2cProductIndex
from tpp.DynamicSiteMiddleware import get_current_site
from usersites.cbv import ItemDetail, ItemList
from usersites.mixins import UserTemplateMixin
from usersites.views import ProductJsonData


class B2CProductList(UserTemplateMixin, ItemList):
    model = B2CProduct
    template_name = '{template_path}/B2CProducts/contentPage.html'
    paginate_by = 16
    filter_key = 'company'
    url_paginator = "b2c_products:paginator"
    current_section = _("B2C Products")
    title = _("B2C Products")

    def dispatch(self, request, *args, **kwargs):
        category_pk = kwargs.pop('pk', None)

        try:
            self.category = B2CProductCategory.objects.get(pk=category_pk)
        except B2CProductCategory.DoesNotExist:
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
        organization = get_current_site().user_site.organization
        categories = B2CProductCategory.objects.filter(products__company_id=organization.pk) \
            .order_by('level').distinct()

        context_data['categories'] = OrderedDict(sorted(
            self._load_category_hierarchy(categories).items(), key=lambda x: [x[1].tree_id, x[1].lft]))

        context_data['selected_category'] = self.category

        if self.category:
            context_data['url_parameter'] = [self.category.slug, self.category.pk]

        return context_data

    def get_url_paginator(self):
        if self.category:
            return "b2c_products:category_paged"

        return self.url_paginator

    def get_queryset(self):
        queryset = super().get_queryset().distinct()

        if self.category:
            if self.category.is_leaf_node():
                categories = [self.category]
            else:
                categories = self.category.get_descendants(include_self=True)

            queryset = queryset.filter(categories__in=categories)

        return queryset



class B2CProductDetail(UserTemplateMixin, ItemDetail):

    model = B2CProduct
    filter_key = 'company'
    template_name = '{template_path}/B2CProducts/detailContent.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.session.get('basket_currency'):
            request.session['basket_currency'] = request.POST.get('currency')

        if not request.session.get('company_paypal'):
            request.session['company_paypal'] = request.POST.get('company_paypal')

        if request.POST.get('quantity').isdigit():
            basket = Basket(request)
            basket.add(request.POST.get('product_id'), request.POST.get('quantity'))
            return HttpResponse(status=200)
        return HttpResponseNotFound()

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        domain = get_current_site().domain

        if self.object.currency and self.object.cost:

            paypal_dict = {
                "business": self.object.company.company_paypal_account or '',
                "amount":  self.object.get_discount_price,
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
            context_data['loop_times']  = range(1, 11)
        return context_data



class B2CProductBasket(View):

    def get(self, request):
        basket      = Basket(request)
        del_product = request.GET.get('del')
        clean       = request.GET.get('clean')

        if basket.summary:
            paypal_dict = {
                'business': basket.paypal,
                'amount': basket.summary,
                'notify_url': 'http://{0}{1}'.format(get_current_site().domain, reverse('paypal-ipn')),
                'return_url': request.build_absolute_uri(),
                'cancel_return': request.build_absolute_uri(),
                'item_name': _('Products from website ') + get_current_site().domain,
                'no_shipping': 0,
                'quantity': 1,
                'currency_code': basket.currency
            }
        else:
            paypal_dict = {}

        data = {
            'title': _('B2C Basket'),
            'basket': dict(src=basket),
            'total': basket.summary,
            'paypal_form': PayPalPaymentsForm(initial=paypal_dict),
        }

        # Delete product form basket
        if del_product:
            product = B2CProduct.objects.get(id=del_product)
            basket.remove(product)
            return HttpResponseRedirect((reverse('b2c_products:basket')))

        # # Clean basket
        if clean:
            if clean.isdigit():
                basket.clear()
                return HttpResponseRedirect((reverse('b2c_products:basket')))
            return HttpResponseNotFound()

        return render(request, 'usersites/B2CProducts/basket.html', data)

    def post(self, request):
        basket     = Basket(request)
        product    = request.POST.getlist('product_id')
        quantity   = request.POST.getlist('quantity')
        update     = dict(zip(product, quantity))

        for product_id, quantity in update.items():
            try:
                if int(quantity) <= 0:
                    break
            except ValueError:
                break

            basket.update(B2CProduct.objects.get(id=product_id), quantity)
        return HttpResponseRedirect((reverse('b2c_products:basket')))



class B2CProductSearch(UserTemplateMixin, ItemList):
    model = B2CProduct
    template_name = '{template_path}/B2CProducts/searchPage.html'
    paginate_by = 16
    filter_key = 'company'
    url_paginator = "b2c_products:serch_paginator"
    current_section = _("B2C Products")
    title = _("B2C Products")

    def get_url_paginator(self):
        return self.url_paginator

    def get_queryset(self):
        q = self.request.GET.get('s') or None
        if q and not re.match("[\!@#$%^&'*]+", q):
            return self.model.get_active_objects().filter(name__icontains=q.strip(), **self.get_filter_kwargs())
        return self.model.get_active_objects().filter(**self.get_filter_kwargs())



class B2CProductByEmail(UserTemplateMixin, FormView):
    template_name = '{template_path}/B2CProducts/orderByEmail.html'
    form_class = OrderEmailForm
    success_url = reverse_lazy('b2c_products:order_done')

    def get_context_data(self, **kwargs):
        basket = Basket(self.request)
        has = basket.count
        context = super(B2CProductByEmail, self).get_context_data(**kwargs)
        context['basket'] = dict(src=basket)
        context['total'] = basket.summary
        return context

    def form_valid(self, form):
        cd = form.cleaned_data
        basket = Basket(self.request)
        org_email = get_current_site().user_site.organization.email
        context = {
            'name': cd['name'],
            'last_name': cd['last_name'],
            'email': cd['email'],
            'message': cd['message'],
            'basket': dict(src=basket),
            'total': '{0} {1}'.format(basket.summary(), basket.currency()),
            'org': get_current_site().user_site.organization,
            'site': get_current_site().domain,
        }

        subject = (_('Order from') + ' {0}').format(get_current_site().domain)
        body = loader.render_to_string('usersites/B2CProducts/templateEmail.html', context)

        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL,
                [org_email, 'migirov@gmail.com'], fail_silently=False)

        return super(B2CProductByEmail, self).form_valid(form)


class B2CProductJsonData(ProductJsonData):
    model_class = B2CProduct
    search_index_class = B2cProductIndex
