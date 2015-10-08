from django import forms
from django.contrib.contenttypes.forms import generic_inlineformset_factory
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from b24online.models import B2BProduct, AdditionalPage
from centerpokupok.models import B2CProduct


class B2BProductForm(forms.ModelForm):
    sku = forms.CharField(required=True)

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