# -*- coding: utf-8 -*-
import re
from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render, render_to_response
from django.template import loader, RequestContext
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.views.generic.edit import FormView
from paypal.standard.forms import PayPalPaymentsForm
from b24online.utils import get_template_with_base_path
from centerpokupok.Basket import Basket
from centerpokupok.forms import OrderEmailForm
from centerpokupok.models import B2CProduct
from tpp.DynamicSiteMiddleware import get_current_site
from usersites.cbv import ItemDetail, ItemList
from usersites.mixins import UserTemplateMixin


def render_page(request, template, **kwargs):
    return render_to_response(get_template_with_base_path(template), kwargs, context_instance=RequestContext(request))


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
    def get(self, request):
        basket = Basket(request)
        del_product = request.GET.get('del')
        clean = request.GET.get('clean')

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
