from django import forms
from django.utils.translation import ugettext as _
from django.forms.extras.widgets import SelectDateWidget

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
