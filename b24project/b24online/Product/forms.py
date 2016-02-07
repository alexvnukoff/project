# -*- encoding: utf-8 -*-

import logging

from django.db import transaction, IntegrityError
from django import forms
from django.core.mail import EmailMessage
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.forms import generic_inlineformset_factory
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.conf import settings

from guardian.shortcuts import get_objects_for_user

from b24online.models import (B2BProduct, AdditionalPage, Organization, 
    DealOrder, Deal, DealItem, Company)
from centerpokupok.models import B2CProduct
from b24online.utils import get_permitted_orgs

logger = logging.getLogger(__name__)


class B2BProductForm(forms.ModelForm):
    sku = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        # first call parent's constructor
        super().__init__(*args, **kwargs)
        # there's a `fields` property now
        self.fields['image'].required = True

        if self.instance.pk:
            self.initial['sku'] = self.instance.sku

    class Meta:
        model = B2BProduct
        fields = ('name', 'description', 'keywords', 'short_description', 'image',
                  'currency', 'measurement_unit', 'cost', 'categories')


class B2CProductForm(forms.ModelForm):
    sku = forms.CharField(required=True)
    start_coupon_date = forms.DateField(input_formats=["%d/%m/%Y"], required=False)
    end_coupon_date = forms.DateField(input_formats=["%d/%m/%Y"], required=False)

    def __init__(self, *args, **kwargs):
        # first call parent's constructor
        super().__init__(*args, **kwargs)

        self.fields['image'].required = True
        self.fields['cost'].required = True
        self.fields['currency'].required = True

        if self.instance.pk:
            self.initial['sku'] = self.instance.sku

            if self.instance.start_coupon_date and self.instance.end_coupon_date:
                self.initial['start_coupon_date'] = self.instance.start_coupon_date.strftime('%d/%m/%Y')
                self.initial['end_coupon_date'] = self.instance.end_coupon_date.strftime('%d/%m/%Y')

    def clean(self):
        cleaned_data = super().clean()
        start_coupon_date = cleaned_data.get("start_coupon_date")
        end_coupon_date = cleaned_data.get("end_coupon_date")
        coupon_discount_percent = cleaned_data.get("coupon_discount_percent")

        if coupon_discount_percent or coupon_discount_percent == 0:
            if coupon_discount_percent < 1:
                self.add_error('coupon_discount_percent', _('Discount can not be smaller than 1 percent'))

            if coupon_discount_percent > 99:
                self.add_error('coupon_discount_percent', _('Discount can not be bigger than 99 percent'))

            if not start_coupon_date:
                self.add_error('start_coupon_date', _('You should provide coupon start date'))

            if not end_coupon_date:
                self.add_error('end_coupon_date', _('You should provide coupon end date'))

            if start_coupon_date and end_coupon_date and start_coupon_date > end_coupon_date:
                self.add_error('start_coupon_date', _('Starting date should be earlier than ending date'))

        elif start_coupon_date or end_coupon_date:
            self.add_error('coupon_discount_percent', _('Coupon discount percrnt should be provided'))

    def clean_discount_percent(self):
        discount_percent = self.cleaned_data.get('discount_percent', None)

        if discount_percent or discount_percent == 0:
            if discount_percent < 1:
                raise ValidationError(_('Discount can not be smaller than 1 percent'))

            if discount_percent > 99:
                raise ValidationError(_('Discount can not be bigger than 99 percent'))

        return discount_percent

    class Meta:
        model = B2CProduct
        fields = ('name', 'description', 'keywords', 'short_description', 'image',
                  'currency', 'cost', 'categories', 'coupon_discount_percent', 'discount_percent')

AdditionalPageFormSet = generic_inlineformset_factory(AdditionalPage, fields=('title', 'content'), max_num=5,
                                                      validate_max=True, extra=0)

class B2_ProductBuyForm(forms.Form):
    """
    The form to add DealItem.
    """
    customer_organization = forms.ChoiceField(label=_('Organization'), 
        required=False, choices=())
    customer_type = forms.ChoiceField(label=_('Customer type'), required=True, 
        widget=forms.RadioSelect, choices=DealOrder.CUSTOMER_TYPES)
    quantity = forms.IntegerField(label=_('Quantity'), 
        required=True)        
    
    def __init__(self, request, product, *args, **kwargs):
        """
        Initialize the fields - customer_type and customer_organization
        """
        super(B2_ProductBuyForm, self).__init__(*args, **kwargs)
        self._request = request        
        self._product = product
        self._supplier = product.company
        self.has_companies = False
        
        # The 'customer_organization' field choices 
        orgs = get_permitted_orgs(request.user, model_klass=Company)
        self.initial['customer_type'] = DealOrder.AS_PERSON
        if orgs:
            self.fields['customer_organization'].choices = \
                ((item.id, item.name) for item in orgs)
            self.has_companies = True
        else:
            del self.fields['customer_organization']
            self.fields['customer_type'].widget = forms.HiddenInput()

        self.initial['quantity'] = 1

    def clean_customer_type(self):
        """
        Get the customer.
        """
        self._customer_type = self.cleaned_data['customer_type']
        if self._customer_type == DealOrder.AS_ORGANIZATION:
            customer_organization = self.data['customer_organization']
            self._customer = customer_organization
        else:
            self._customer = self._request.user
        return self._customer_type

    def send_notification(self, deal_item):
        """
        Send the notications.
        """        
        notification_template = getattr(settings, 'DEAL_NOTICATION_TEMPLATE')
        email = deal_item.deal.supplier_company.email
        if notification_template and email:
            context = {
                'deal_item': deal_item, 
            }
            supplier = deal_item.deal.supplier_company
            message = render_to_string(notification_template, context)
            subject = _('The info about ordered product. %(deal)s') \
                % {'deal': deal_item.deal}
            mail = EmailMessage(
                subject,
                message,
                'noreply@tppcenter.com',
                [email, 'orders@b24online.com']
            )
            mail.send()

    def save(self):
        """
        Save deal and it's new item.
        """
        try:
            with transaction.atomic():
                if self._customer_type == DealOrder.AS_ORGANIZATION:
                    deal_order, created = DealOrder.objects\
                        .get_or_create(
                            customer_type=self._customer_type,
                            customer_organization_id=self._customer, 
                            status=DealOrder.DRAFT)
                else:
                    deal_order, created = DealOrder.objects\
                        .get_or_create(
                            customer_type=self._customer_type,
                            created_by=self._customer, 
                            status=DealOrder.DRAFT)
                if created or not deal_order.total_cost:
                    deal_order.total_cost = 0
                deal_order.total_cost += \
                    self._product.cost * self.cleaned_data['quantity']
                deal_order.created_by = self._request.user
                deal_order.save()

                deal, created = Deal.objects\
                    .get_or_create(
                        deal_order=deal_order,
                        supplier_company=self._supplier,
                        status=DealOrder.DRAFT)
                if created or not deal.total_cost:
                    deal.total_cost = 0
                deal.total_cost += \
                    self._product.cost * self.cleaned_data['quantity']
                deal.created_by = self._request.user
                deal.save()

                model_type = ContentType.objects.get_for_model(self._product)
                deal_item = DealItem.objects\
                    .create(
                        deal=deal,
                        content_type=model_type,
                        object_id=self._product.pk,
                        quantity=self.cleaned_data['quantity'],
                        currency=self._product.currency,
                        cost=self._product.cost)
        except IntegrityError:
            raise
        else:
            self.send_notification(deal_item)
        return deal_order
        

class DealPaymentForm(forms.ModelForm):

    agree = forms.BooleanField(label=_('Agree with license conditions'),
        required=True)
                        
    def __init__(self, request, *args, **kwargs):
        super(DealPaymentForm, self).__init__(*args, **kwargs)
        self.request = request
        for field_name in self.fields:
            self.fields[field_name].required = True
        user = request.user
        if user.is_authenticated():
            self.initial['person_first_name'] = user.profile.first_name
            self.initial['person_last_name'] = user.profile.last_name
            self.initial['person_country'] = user.profile.country
            self.initial['person_email'] = user.email

    class Meta:
        model = Deal
        fields = (
            'person_first_name',
            'person_last_name',
            'person_phone_number',
            'person_country',
            'person_address',
            'person_email',
            'agree',
        )
        
    def save(self, *args, **kwargs):
        super(DealPaymentForm, self).save(*args, **kwargs)
        self.instance.pay()
        return self.instance
