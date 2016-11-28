# -*- encoding: utf-8 -*-

import re
import logging

from django.db import transaction, IntegrityError
from django.db.models import Q
from django import forms
from django.core.mail import EmailMessage
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.forms import generic_inlineformset_factory
from django.core.urlresolvers import reverse
from django.forms import modelformset_factory
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.conf import settings

from guardian.shortcuts import get_objects_for_user

from b24online.models import (B2BProduct, AdditionalPage, Organization,
    DealOrder, Deal, DealItem, Company, Producer)
from centerpokupok.models import B2CProduct
from b24online.utils import get_permitted_orgs
from b24online.widgets import JsTreeInput

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
        fields = ('name', 'description', 'keywords', 'short_description',
                  'image', 'currency', 'measurement_unit', 'cost',
                  'producer', 'categories')


class B2CProductForm(forms.ModelForm):
    sku = forms.CharField(required=True)
    start_coupon_date = forms.DateField(input_formats=["%d/%m/%Y"], required=False)
    end_coupon_date = forms.DateField(input_formats=["%d/%m/%Y"], required=False)
    additional_image = forms.CharField(required=False)

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
        fields = ('name', 'description', 'keywords', 'short_description',
                  'image', 'currency', 'cost', 'categories',
                  'coupon_discount_percent', 'discount_percent',
                  'producer', 'additional_images', 'show_on_main')

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
        Send the notifications.
        """
        notific_disable = getattr(settings, 'ORDER_NOTIFICATION_DISABLE')
        notific_template = getattr(settings, 'ORDER_NOTIFICATION_TEMPLATE')
        notific_from = getattr(settings, 'ORDER_NOTIFICATION_FROM')
        notific_to = getattr(settings, 'ORDER_NOTIFICATION_TO')
        email = deal_item.deal.supplier_company.email
        if not notific_disable and all((notific_template, notific_from,
                                        notific_to)):
            message = render_to_string(notific_template,
                                       {'deal_item': deal_item,})
            subject = _('The info about ordered product. %(deal)s') \
                        % {'deal': deal_item.deal}
            recipients = [notific_to]
            if email:
                recipients.append(email)
            mail = EmailMessage(subject, message, notific_from,
                                recipients)
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
                deal_order.created_by = self._request.user
                deal_order.save()
                deal, created = Deal.objects\
                    .get_or_create(
                        deal_order=deal_order,
                        currency=self._product.currency,
                        supplier_company=self._supplier,
                        status=DealOrder.DRAFT,
                        created_by=self._request.user)

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
            self.initial['person_phone_number'] = user.profile.mobile_number

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


class DealListFilterForm(forms.Form):
    """
    The search form for :class:`Deal`.
    """
    customer_name = forms.CharField(
        label=_('Customer (person or company)'),
        required=False
    )
    product_name = forms.CharField(
        label=_('Product'),
        required=False
    )
    start_date = forms.DateField(
        label=_('From'),
        input_formats=["%d/%m/%Y"],
        widget=forms.DateInput(format = '%d/%m/%Y'),
        required=False
    )
    end_date = forms.DateField(
        label=_('Till'),
        input_formats=["%d/%m/%Y"],
        widget=forms.DateInput(format = '%d/%m/%Y'),
        required=False
    )

    def __init__(self, *args, **kwargs):
        """
        Set the initial values.
        """
        super(DealListFilterForm, self).__init__(*args, **kwargs)
        self.fields['start_date'].widget.attrs.update({'class': 'date'})
        self.fields['end_date'].widget.attrs.update({'class': 'date'})

    def filter(self, qs):
        """
        Filter the qs.
        """
        customer_name, product_name, start_date, end_date,  = \
            list(map(lambda x: self.cleaned_data.get(x), self.fields.keys()))
        if start_date:
            qs = qs.filter(created_at__gte=start_date)
        if end_date:
            qs = qs.filter(created_at__lte=end_date)
        if customer_name:
            qs = qs.filter(
                (Q(deal_order__customer_type=DealOrder.AS_PERSON,
                   deal_order__created_by__profile__isnull=False) & \
                (Q(deal_order__created_by__profile__first_name__icontains=\
                    customer_name) | \
                 Q(deal_order__created_by__profile__last_name__icontains=\
                       customer_name))) | \
                 Q(deal_order__customer_type=DealOrder.AS_ORGANIZATION,
                   deal_order__customer_organization__company__isnull=False,
                   deal_order__customer_organization__company__name__icontains=\
                       customer_name))
        return qs


    def colorize(self, wrapped_value):
        value = wrapped_value.value
        q_name = wrapped_value.q_name
        if q_name == 'customer_name':
            q = self.cleaned_data.get('customer_name')
            if q:
                q_replace = '<span style="color: red;">{0}</span>' . format(q)
                return str(value).replace(q, q_replace)
        elif q_name == 'deal_date':
            start_date = self.cleaned_data.get('start_date')
            end_date = self.cleaned_data.get('end_date')
            if start_date or end_date:
                colorized_value = re.sub(
                    r'(\d{1,2}\/\d{1,2}\/\d{1,4})',
                    r'<span style="color: red;">\1</span>',
                    value
                )
                return colorized_value
        return value


# The formset for products in Basket
DealItemFormSet = modelformset_factory(
    DealItem,
    fields=('quantity',),
    can_delete=True,
    widgets={'quantity': forms.NumberInput(attrs={'min': '1'}),},
    extra=0
)


class DealOrderedForm(forms.ModelForm):

    paid = forms.BooleanField(
        label=_('Already paid'),
        required=False)

    reject = forms.BooleanField(
        label=_('Reject deal'),
        required=False)

    class Meta:
        model = Deal
        fields = ()

    def save(self):
        paid = self.cleaned_data.get('paid')
        reject = self.cleaned_data.get('reject')
        if paid or reject:
            if paid:
                self.instance.status = Deal.PAID
            elif reject:
                self.instance.status = Deal.REJECTED
            self.instance.save()


DealOrderedFormSet = modelformset_factory(
    Deal,
    fields=(),
    can_delete=False,
    extra=0
)


# The formsets for B2B and B2C products
B2BProductFormSet = modelformset_factory(
    B2BProduct,
    fields=('name', 'categories', 'currency', 'cost'),
    widgets={
        'name': forms.Textarea(attrs={'rows': '3', 'cols': '30'}),
        'categories': forms.SelectMultiple(attrs={'class': 'select-categories'}),
    },
    extra=0,
)

B2CProductFormSet = modelformset_factory(
    B2CProduct,
    fields=('name', 'categories', 'currency', 'cost'),
    widgets={
        'name': forms.Textarea(attrs={'rows': '3', 'cols': '30'}),
        #'categories': forms.TextInput(attrs={'class': 'select-categories'}),
        'categories': forms.SelectMultiple(attrs={'class': 'select-categories'}),
    },
    extra=0
)


class ProducerForm(forms.ModelForm):

    class Meta:
        model = Producer
        fields = ['name', 'logo', 'b2b_categories', 'b2c_categories']

    def __init__(self, *args, **kwargs):
        super(ProducerForm, self).__init__(*args, **kwargs)
        self.content_type = ContentType.objects.get_for_model(Producer)
        self.fields['name'].widget = forms.Textarea(
            attrs={'rows': '2', 'cols': '50'}
        )
        self.fields['b2b_categories'].widget = JsTreeInput(
            attrs={'data-url': reverse('products:category_tree_json', 
                kwargs={'b2_type': 'b2b'})})
        self.fields['b2c_categories'].widget = JsTreeInput(
            attrs={'data-url': reverse('products:category_tree_json', 
                kwargs={'b2_type': 'b2c'})})
        self.fields['b2b_categories'].required = False
        self.fields['b2c_categories'].required = False


class ExtraParamsForm(forms.Form):
    """The form for B2C Product's additional paramenter."""

    LANGUAGES = ('en', 'ru', 'am', 'bg', 'uk', 'he', 'ar', 'zh', 'es')
    
    name = forms.RegexField(
        label=_('Field name'),
        regex='^\w+$',
        required=True, 
        max_length=100
    )
    label = forms.CharField(
        label=_('Field label'),
        required=False, 
        widget=forms.Textarea(attrs={'rows': '2', 'cols': '50'}),
    )
    fieldtype = forms.ChoiceField(
        label=_('Field type'),
        required=True,
        choices=((x, x) for x in ('char', 'textarea', 'image')),
        widget=forms.Select(attrs={'style': 'width: 50%;'})
    )
    is_required = forms.BooleanField(
        label=_('Is field required'),
        required=False
    )
    pre_text = forms.CharField(
        label=_('Text before the field'),
        required=False, 
        widget=forms.Textarea(attrs={'rows': '2', 'cols': '50'}),
    )
    post_text = forms.CharField(
        label=_('Text after the field'),
        required=False, 
        widget=forms.Textarea(attrs={'rows': '2', 'cols': '50'}),
    )

    def __init__(self, object, field_name=None, *args, **kwargs):
        self.object = object
        super(ExtraParamsForm, self).__init__(*args, **kwargs)

        self._data = dict((item.get('name'), item) for item in \
            self.object.get_extra_params()) or {}
        self.field_name = field_name if self.object.extra_params \
            and field_name in self._data else None

        for lang in self.LANGUAGES:
            self.fields['initial_{0}' . format(lang)] = \
                forms.CharField(
                    label=_('Initial field value for lang') \
                        + ' &laquo;<span style="color: red;">{0}</span>&raquo;' \
                        . format(lang),
                    required=False, 
                    widget=forms.Textarea(attrs={'rows': '7', 'cols': '50'}),
                )
        if self._data and field_name and field_name in self._data:
            _values = self._data[field_name]
            for f_name, f_value in _values.items():
                if f_name == 'initial' and isinstance(f_value, (tuple, list)):
                    for s_lang, s_value in f_value:
                        if s_lang in self.LANGUAGES:
                            logger.debug(s_value)
                            s_value = s_value.replace('\\n', '\n')
                            self.initial['initial_{0}' . format(s_lang)] = \
                                s_value
                else:
                    if f_name in self.fields:
                        self.initial[f_name] = f_value

    def save(self, *args, **kwargs):
        if not self.object.extra_params:
            self.object.extra_params = []
        data = {}
        for f_name, f_value in self.cleaned_data.items():
            if f_name.startswith('initial_'):
                data.setdefault('initial', [])
                f_lang = f_name[len('initial_'):]
                f_value = f_value.replace('\n', '\\n')
                data['initial'].append((f_lang, f_value))
            else:
                data[f_name] = f_value
        if data:
            if self.object.extra_params and self.field_name:
                has_found = False
                result = []
                for item in self.object.extra_params:
                    f_name = item['name']
                    if f_name == self.field_name:
                        has_found = True
                        result.append(data)
                    else:
                        result.append(item)
                if not has_found:
                    result.append(data)
                self.object.extra_params = result
            elif 'name' in self.cleaned_data:
                f_name = self.cleaned_data['name']
                self.object.extra_params.append(data)
            self.object.save()
