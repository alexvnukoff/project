# -*- coding: utf-8 -*-
from django import forms
from centerpokupok.models import B2CBasket

class B2CProductForm(forms.ModelForm):
    class Meta:
        model = B2CBasket
        fields = ['product_id', 'quantity',]