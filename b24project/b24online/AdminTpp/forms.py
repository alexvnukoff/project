# -*- encoding: utf-8 -*-
from django import forms
from b24online.models import Country, Branch, B2BProductCategory, AdvertisementPrice, BannerBlock
from centerpokupok.models import B2CProductCategory


class CountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = ('name',)


class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ('name',)


class B2BProductCategoryForm(forms.ModelForm):
    class Meta:
        model = B2BProductCategory
        fields = ('name',)


class B2CProductCategoryForm(forms.ModelForm):
    class Meta:
        model = B2CProductCategory
        fields = ('name',)


class AdvertisementPricesForm(forms.ModelForm):
    class Meta:
        model = AdvertisementPrice
        fields = ('price',)


class BannerBlockForm(forms.ModelForm):
    class Meta:
        model = BannerBlock
        fields = ('width', 'height', 'factor', 'name')
