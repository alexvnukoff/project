# -*- encoding: utf-8 -*-

import re
import logging
import json

from collections import OrderedDict

from django.db import transaction, IntegrityError
from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render_to_response
from django.template import loader, RequestContext
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.contrib.contenttypes.models import ContentType

from paypal.standard.forms import PayPalPaymentsForm
from b24online.utils import get_template_with_base_path
from centerpokupok.Basket import Basket
from centerpokupok.forms import OrderEmailForm, DeliveryForm
from centerpokupok.models import B2CProduct, B2CProductCategory
from b24online.models import (Questionnaire, DealOrder, Deal, DealItem)
from b24online.search_indexes import B2cProductIndex
from tpp.DynamicSiteMiddleware import get_current_site
from usersites.cbv import ItemDetail
from usersites.mixins import UserTemplateMixin
from usersites.views import ProductJsonData
from usersites.forms import create_extra_form
from usersites.B2CProducts.forms import PayPalBasketForm


logger = logging.getLogger(__name__)


class B2CProductDetail(UserTemplateMixin, ItemDetail):
    model = B2CProduct
    filter_key = 'company'
    template_name = '{template_path}/B2CProducts/detailContent.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object: 
            questionnaire = Questionnaire.get_questionnaire(self.object)
            if questionnaire:
                return HttpResponseRedirect(reverse(
                    'questionnaires:detail',
                    kwargs={'item_id': questionnaire.id}
                ))
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        cls = type(self)
        self.object = self.get_object()
        if not request.session.get('basket_currency'):
            request.session['basket_currency'] = request.POST.get('currency')

        if not request.session.get('company_paypal'):
            request.session['company_paypal'] = request.POST.get('company_paypal')

        if 'quantity' in request.POST and request.POST.get('quantity').isdigit():
            basket = Basket(request)
            extra_params_values = cls.get_extra_params(request)
            basket_item = basket.add(
                request.POST.get('product_id'), 
                request.POST.get('quantity'),
                extra_params=extra_params_values,
            )
            return HttpResponse(status=200)

        elif 'presave' in request.POST:
            context = self.get_context_data(**kwargs) or {}
            return self.render_to_response(context)
        return HttpResponseNotFound()
        
    @classmethod
    def get_extra_params(cls, request):
        data = None
        if request.method == 'POST':
            extra_params_uuid = request.POST.get('extra_params_uuid')
            if extra_params_uuid:
                uuid_key = 'extra_params__{0}' . format(extra_params_uuid)
                data = request.session.get(uuid_key)
        return data        

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        domain = get_current_site().domain

        extra_form = create_extra_form(self.object, self.request)
        if extra_form:
            if self.request.method == 'POST' and extra_form.is_valid():
                extra_form.save()
                context_data['extra_params_uuid'] = \
                    extra_form.cleaned_data.get('extra_params_uuid')
            else:
                context_data['extra_form'] = extra_form

        if self.object.currency and self.object.cost:
            paypal_dict = {
                "business": self.object.company.company_paypal_account or '',
                "amount": self.object.get_discount_price,
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
            context_data['loop_times'] = range(1, 11)
        return context_data


class B2CProductBasket(View):
    template_name = 'B2CProducts/basket.html'

    def get(self, request):
        # Корзина
        basket = Basket(request)
        
        # Действия
        del_product = request.GET.get('del')
        clean = request.GET.get('clean')

        # Сколько наименований товаров в Корзине
        basket_items_total = len(list(basket))

        # Набор информации для PayPal
        paypal_dict = {}
        if basket_items_total > 1:
            paypal_dict.update({
                'cmd': '_cart',
                'upload': 1,
                'business': basket.paypal,
                'notify_url': 'http://{0}{1}'.format(get_current_site().domain, reverse('paypal-ipn')),
                'return_url': request.build_absolute_uri(),
                'cancel_return': request.build_absolute_uri(),
                'no_shipping': 0,
                'quantity': 1,
                'currency_code': basket.currency
            })
            i = 1
            for item in basket:
                paypal_dict['amount_%d' % i] = \
                    item.product.get_discount_price() * item.quantity
                paypal_dict['item_name_%d' % i] = item.product.name
                i += 1    
            paypal_form = PayPalBasketForm(basket, initial=paypal_dict)

        else:
            if basket.summary:
                paypal_dict.update({
                    'business': basket.paypal,
                    'amount': basket.summary,
                    'notify_url': 'http://{0}{1}'.format(get_current_site().domain, reverse('paypal-ipn')),
                    'return_url': request.build_absolute_uri(),
                    'cancel_return': request.build_absolute_uri(),
                    'item_name': _('Products from website ') + get_current_site().domain,
                    'no_shipping': 0,
                    'quantity': 1,
                    'currency_code': basket.currency
                })
            paypal_form = PayPalPaymentsForm(initial=paypal_dict)

        data = {
            'title': _('B2C Basket'),
            'basket': dict(src=basket),
            'total': basket.summary,
            'paypal_form': paypal_form,
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
        return render_to_response(
            get_template_with_base_path(self.template_name),
            data,
            context_instance=RequestContext(request)
        )

    def post(self, request):
        basket = Basket(request)
        product = request.POST.getlist('product_id')
        quantity = request.POST.getlist('quantity')
        update = dict(zip(product, quantity))

        for product_id, quantity in update.items():
            try:
                if int(quantity) <= 0:
                    break
            except ValueError:
                break

            basket.update(B2CProduct.objects.get(id=product_id), quantity)
        return HttpResponseRedirect((reverse('b2c_products:basket')))


class B2CProductByEmail(UserTemplateMixin, FormView):
    template_name = '{template_path}/B2CProducts/orderByEmail.html'
    form_class = OrderEmailForm
    success_url = reverse_lazy('b2c_products:order_done')

    def get_form_kwargs(self):
        kwargs = super(B2CProductByEmail, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

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

        if not getattr(settings, 'NOT_SEND_EMAIL', False):
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL,
                      [org_email, 'migirov@gmail.com'], fail_silently=False)

        # Save the bought products to Deal and DealItems
        self.save_deal_order(basket, data=cd)
        return super(B2CProductByEmail, self).form_valid(form)

    def save_deal_order(self, basket, data={}):
        """
        Save the basket items to DealItems    
        """
        # Product supplier company
        supplier = get_current_site().user_site.organization
        try:
            with transaction.atomic():
                # Deal order
                deal_order = DealOrder.objects.create(
                    customer_type=DealOrder.AS_PERSON,
                    status=DealOrder.READY,
                    deal_place=DealOrder.ON_USERSITE
                )
                deal_order.save()

                for item in basket:
                    deal = Deal.objects.create(
                        deal_order=deal_order,
                        currency=item.product.currency,
                        supplier_company=supplier,
                        person_last_name=data.get('name'),
                        person_email=data.get('email'),
                        person_address=data.get('address'),
                        person_phone_number=data.get('phone'),
                        status=Deal.ORDERED,
                    )
                    model_type = ContentType.objects.get_for_model(item.product)
                    deal_item = DealItem.objects.create(
                        deal=deal,
                        content_type=model_type,
                        object_id=item.product.pk,
                        quantity=item.quantity,
                        currency=item.product.currency,
                        cost=item.product.cost,
                        extra_params=item.extra_params,
                    )
        except IntegrityError:
            raise
        return deal_order


class B2CProductJsonData(ProductJsonData):
    model_class = B2CProduct
    search_index_class = B2cProductIndex


class B2C_orderDone(UserTemplateMixin, TemplateView):
    template_name = '{template_path}/B2CProducts/orderDone.html'

    def get_queryset(self):
        return get_current_site().user_site.organization.additional_pages.all()


class B2CProductDelivery(UserTemplateMixin, FormView):
    template_name = '{template_path}/B2CProducts/delivery.html'
    form_class = DeliveryForm
    success_url = reverse_lazy('b2c_products:basket')

    def get_form_kwargs(self):
        kwargs = super(B2CProductDelivery, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(B2CProductDelivery, self).get_context_data(**kwargs)
        try:
            product = B2CProduct.objects\
                .get(pk=int(self.request.GET.get('product_id')))
        except (TypeError, ValueError, B2CProduct.DoesNotExist) as exc:
            product = None

        domain = get_current_site().domain
        if not product:    
            basket = Basket(self.request)
            has = basket.count
            context['basket'] = dict(src=basket)
            context['total'] = basket.summary

            # Сколько наименований товаров в Корзине
            basket_items_total = len(list(basket))

            # Набор информации для PayPal
            paypal_dict = {}
            if basket_items_total > 1:
                paypal_dict.update({
                    'cmd': '_cart',
                    'upload': 1,
                    'business': basket.paypal,
                    'notify_url': 'http://{0}{1}'.format(domain, reverse('paypal-ipn')),
                    'return_url': self.request.build_absolute_uri(),
                    'cancel_return': self.request.build_absolute_uri(),
                    'no_shipping': 0,
                    'quantity': 1,
                    'currency_code': basket.currency
                })
                i = 1
                for item in basket:
                    paypal_dict['amount_%d' % i] = \
                        item.product.get_discount_price() * item.quantity
                    paypal_dict['item_name_%d' % i] = item.product.name
                    i += 1    
                paypal_form = PayPalBasketForm(basket, initial=paypal_dict)
            else:
                if basket.summary:
                    paypal_dict.update({
                        'business': basket.paypal,
                        'amount': basket.summary,
                        'notify_url': 'http://{0}{1}'.format(domain, reverse('paypal-ipn')),
                        'return_url': self.request.build_absolute_uri(),
                        'cancel_return': self.request.build_absolute_uri(),
                        'item_name': _('Products from website ') + domain,
                        'no_shipping': 0,
                        'quantity': 1,
                        'currency_code': basket.currency
                    })
                paypal_form = PayPalPaymentsForm(initial=paypal_dict)
        else:
            try:
                quantity = int(self.request.GET.get('quantity'))
            except ValueError as exc:
                quantity = 0
            
            context.update({'product': product, 'quantity': quantity})
            if product.currency and product.cost and quantity:
                paypal_dict = {
                    "business": product.company.company_paypal_account or '',
                    "amount": product.get_discount_price,
                    "notify_url": "http://%s%s" % (domain, reverse('paypal-ipn')),
                    "return_url": self.request.build_absolute_uri(),
                    "cancel_return": self.request.build_absolute_uri(),
                    "item_number": product.pk,
                    "item_name": product.name,
                    "no_shipping": 0,
                    "quantity": 1,
                    "currency_code": product.currency
                }
                paypal_form = PayPalPaymentsForm(initial=paypal_dict)
        context.update({'paypal_form': paypal_form,})
        return context


def delivery_info_json(request, **kwargs):
    if request.is_ajax():
        data = {}
        if request.method == 'POST':
            form = DeliveryForm(
                request=request, 
                data=request.POST,
                files=request.FILES
            )
            if form.is_valid():
                form.save()
                data.update({
                    'code': 'success',
                    'msg': _('You have successfully add new participant'),
                })
            else:
                data.update({
                    'code': 'error',
                    'errors': form.get_errors(),
                    'msg': _('There are some errors'),
                })
            return HttpResponse(
                json.dumps(data), 
                content_type='application/json'
            )
    return HttpResponseBadRequest()
