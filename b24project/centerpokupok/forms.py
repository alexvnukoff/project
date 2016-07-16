# -*- encoding: utf-8 -*-

import logging

from django import forms
from django.utils.translation import ugettext as _
from django.forms.extras.widgets import SelectDateWidget

logger = logging.getLogger(__name__)


class OrderForm(forms.Form):
      recipient_name = forms.CharField(required=True, label=_("Recipient name"))
      city = forms.CharField(required=True, label=_("City"))
      country = forms.CharField(required=True, label=_("Country"))
      zipcode = forms.CharField(required=True, label=_("Zipcode"))
      address = forms.CharField(required=True, label=_("Address"))
      telephone_number = forms.CharField(required=True, label=_("Telephone"))

      def __init__(self,  *args, **kwargs):
         super(OrderForm, self).__init__(*args, **kwargs)
         for title, field  in self.fields.items():
             field.widget.attrs.update({'class': 'textcheck'})


class UserDetail(forms.Form):
    first_name = forms.CharField(required=False, label=_("Fisrt name"))
    first_name.widget.attrs.update({'class': 'textcheck'})
    last_name = forms.CharField(required=False, label=_("Last name"))
    last_name.widget.attrs.update({'class': 'textcheck'})
    birthday = forms.DateField(required=False, label=_("Birthday"))
    birthday.widget.attrs.update({'class': 'textcheck'})
    birthday.widget.input_type = 'date'


class OrderEmailForm(forms.Form):
    """The form class for orders by email"""
    name = forms.CharField(required=True, label=_("Name"))
    last_name = forms.CharField(required=False, label=_("Last Name"))
    email = forms.CharField(required=True, label=_("Email"))
    address = forms.CharField(label=_('Address'), required=False,
                              widget=forms.Textarea)
    phone = forms.CharField(label=_('Contact phone'), required=False)
    message = forms.CharField(label=_("Description"), widget=forms.Textarea)
    
    def __init__(self, *args, **kwargs):
        self._request = kwargs.pop('request')
        super(OrderEmailForm, self).__init__(*args, **kwargs)

        self.need_delivery = True if self._request.GET.get('need_delivery') \
            else False 
                
        # Add the 'placeholders' to the fields
        self.fields['name'].widget.attrs.update(
            {'placeholder': 'Your Name'}
        )
        self.fields['email'].widget.attrs.update(
            {'placeholder': 'Email'}
        )
        self.fields['message'].widget.attrs.update(
            {'placeholder': 'Message'}
        )

        if self.need_delivery:
            self.fields['address'].requesired = True
            self.fields['address'].widget.attrs.update(
                {'placeholder': 'Adress', 'rows': 4}
            )
            self.fields['phone'].requesired = True
            self.fields['phone'].widget.attrs.update(
                {'placeholder': 'Phone'}
            )
        else:
            del self.fields['address']
            del self.fields['phone']
            