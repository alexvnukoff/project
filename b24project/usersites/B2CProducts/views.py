# -*- coding: utf-8 -*-
import uuid
from collections import OrderedDict

from django.contrib.sites.shortcuts import get_current_site
from django.core.urlresolvers import reverse
from django.db.models import F, Sum, IntegerField
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from paypal.standard.forms import PayPalPaymentsForm

from centerpokupok.models import B2CProduct, B2CProductCategory, B2CBasket
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
        categories = B2CProductCategory.objects.filter(products__company_id=organization.pk) \
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


class B2CProductBasket(View):
    def get(self, request):
        if not request.session.get('basket_hash'):
            request.session['basket_hash'] = str(uuid.uuid4())

        product_id = request.GET.get('pk')
        quantity = request.GET.get('q')
        get_stat = request.GET.get('get_stat')
        del_product = request.GET.get('del')
        clean = request.GET.get('clean')

        # Adding product to basket
        if product_id and quantity:
            try:
                product_id = int(product_id)
            except ValueError:
                return HttpResponseNotFound()

            product = get_object_or_404(B2CProduct, pk=product_id)

            # Create a new product row or update existing quantity
            B2CBasket.objects.update_or_create(user_uuid=request.session['basket_hash'],
                                               product=product,
                                               site=get_current_site(request),
                                               ordered=False,
                                               defaults={'quantity': quantity})

            data = B2CBasket.objects.filter(user_uuid=request.session['basket_hash'], ordered=False,
                                            site=get_current_site(request)).aggregate(Sum('quantity'))
            return JsonResponse(data, status=200)

        # Getting basket count only if has basket_hash
        if request.session.get('basket_hash') and get_stat == '1':
            data = B2CBasket.objects.filter(user_uuid=request.session.get('basket_hash'), ordered=False,
                                            site=get_current_site(request)).aggregate(Sum('quantity'))
            if data['quantity__sum'] is not None:
                return JsonResponse(data, status=200)

            return HttpResponse(status=403)

        # List of products
        basket_list = B2CBasket.objects.filter(
            user_uuid=request.session['basket_hash'],
            site=get_current_site(request),
            ordered=False)

        total_price = basket_list.aggregate(
            total=Sum(F('quantity') * F('product__cost'), output_field=IntegerField()))

        item = basket_list.first()

        if item:
            paypal_dict = {
                'business': item.product.company.company_paypal_account,
                'amount': total_price['total'],
                'notify_url': 'http://{0}{1}'.format(get_current_site(request).domain, reverse('paypal-ipn')),
                'return_url': request.build_absolute_uri(),
                'cancel_return': request.build_absolute_uri(),
                'item_name': _('Products from website ') + get_current_site(request).domain,
                'no_shipping': 0,
                'quantity': 1,  # basket_list.count makes a multiplication ;-)
                'currency_code': item.product.currency
            }
        else:
            paypal_dict = {}

        data = {
            'title': _('B2C Basket'),
            'products': [row.product for row in basket_list],
            'price': total_price,
            'paypal_form': PayPalPaymentsForm(initial=paypal_dict),
        }

        # Delete product form basket
        if del_product:
            B2CBasket.objects.filter(product_id=del_product, site=get_current_site(request),
                                         user_uuid=request.session['basket_hash']).delete()

            return HttpResponseRedirect((reverse('b2c_products:basket')))

        # Clean basket
        if clean:
            if clean.isdigit():
                B2CBasket.objects.filter(
                    user_uuid=request.session['basket_hash'],
                    site=get_current_site(request)).delete()

                return HttpResponseRedirect((reverse('b2c_products:basket')))

            return HttpResponseNotFound()

        return render(request, 'usersites/B2CProducts/basket.html', data)

    def post(self, request):
        product = request.POST.getlist('product_id')
        quantity = request.POST.getlist('quantity')
        basket = dict(zip(product, quantity))

        for product_id, quantity in basket.items():
            try:
                if int(quantity) <= 0:
                    break
            except ValueError:
                break

            # TODO refactor it, should not be in loop
            B2CBasket.objects.filter(user_uuid=request.session['basket_hash'],
                                     product_id=int(product_id),
                                     site=get_current_site(request),
                                     ordered=False).update(quantity=int(quantity))

        return HttpResponseRedirect((reverse('b2c_products:basket')))

        # @never_cache
        # def B2CProductBasket(request):

        #                 # Enter the valid credentials for Redis server
        #     r           = redis.StrictRedis(host='localhost', port=6379, db=2)
        #     user_uuid     = request.user.pk
        #     basket_name = 'nyawesomebasket_' + str(user_uuid)
        #     domain      = get_current_site(request).domain

        #     if request.method == 'POST':

        #         jdata       = json.loads(request.body.decode('utf-8'))
        #         product_id  = jdata['product_id']

        #         if product_id:
        #             r.sadd(basket_name, product_id)
        #         else:
        #             r.srem(basket_name, product_id)
        #         return JsonResponse({'basket_count': r.scard(basket_name)}, status=200)

        #     else:
        #         if request.GET.get('count'):
        #             return JsonResponse({'basket_count': r.scard(basket_name)}, status=200)
        #         if request.GET.get('delete'):
        #             r.delete(basket_name)
        #             return HttpResponse(status=200)

        #         basket_list = B2CProduct.objects.filter(pk__in=r.smembers(basket_name))

        #         if basket_list:
        #             paypal_dict = {
        #                 'business': basket_list[0].company.company_paypal_account,
        #                 'amount': 'replace_on_js',
        #                 'notify_url': 'http://{0}{1}'.format(domain, reverse('paypal-ipn')),
        #                 'return_url': request.build_absolute_uri(),
        #                 'cancel_return': request.build_absolute_uri(),
        #                 'item_name': _('Products from website ') + domain,
        #                 'no_shipping': 0,
        #                 'quantity': 1, # basket_list.count makes a multiplication ;-)
        #                 'currency_code': basket_list[0].currency
        #                 }
        #         else:
        #             paypal_dict = {}

        #         data = {
        #             'title': _('B2C Basket'),
        #             'basket_list': basket_list,
        #             'paypal_form': PayPalPaymentsForm(initial=paypal_dict)
        #             }

        #         return render(request, 'usersites/B2CProducts/basket.html', data)
