from django import forms
from django.contrib.contenttypes.forms import generic_inlineformset_factory

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

    def __init__(self, *args, **kwargs):
        # first call parent's constructor
        super().__init__(*args, **kwargs)
        # there's a `fields` property now
        self.fields['image'].required = True
        self.fields['cost'].required = True
        self.fields['currency'].required = True

        if self.instance.pk:
            self.initial['sku'] = self.instance.sku

    class Meta:
        model = B2CProduct
        fields = ('name', 'description', 'keywords', 'short_description', 'image',
                  'currency', 'cost', 'categories')

AdditionalPageFormSet = generic_inlineformset_factory(AdditionalPage, fields=('title', 'content'), max_num=5,
                                                      validate_max=True, extra=0)
