# -*- encoding: utf-8 -*-

"""The forms for B2CProduct"""

import logging

from django import forms
from paypal.standard.forms import PayPalPaymentsForm


logger = logging.getLogger(__name__)


class PayPalBasketForm(PayPalPaymentsForm):
    """The class realizes the 'Add to basket' possibility"""
    
    upload = forms.IntegerField(widget=forms.HiddenInput())
    
    def __init__(self, basket, button_type='add_to_cart', *args, **kwargs):
        super(PayPalBasketForm, self).__init__(
            button_type='buy', 
            *args, 
            **kwargs
        )
        self.initial['cmd'] = '_cart'
        self.basket = basket
        del self.fields['quantity']

    def get_image(self):
        return 'https://www.paypalobjects.com/en_GB/i/btn/x-click-but22.gif'
