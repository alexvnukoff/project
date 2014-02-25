from django import forms
from appl.models import Country
from core.models import Dictionary
from appl import func
from django.utils.translation import ugettext as _
from django.forms.extras.widgets import SelectDateWidget
from tpp.SiteUrlMiddleWare import get_request




class ProfileForm(forms.Form):
      image = forms.ImageField(required=False)

      last_name = forms.CharField(required=True, label=_("Last name"))
      last_name.widget.attrs.update({'class': 'text'})


      first_name = forms.CharField(required=False, label=_("First name"))
      first_name.widget.attrs.update({'class': 'text'})

      middle_name = forms.CharField(required=False, label=_("Middle name"))
      middle_name.widget.attrs.update({'class': 'text'})

      countries = func.getItemsList("Country", 'NAME')
      countries = ([(id, country['NAME'][0]) for id, country in countries.items()])
      country = forms.ChoiceField(required=False, widget=forms.Select(), choices=countries)

      dictSex = Dictionary.objects.get(title='SEX')
      slots = tuple(dictSex.getSlotsList().values_list("id", "title"))
      sex  = forms.ChoiceField(required=True, widget=forms.RadioSelect, choices=slots)

      dictStatus = Dictionary.objects.get(title='PERSONAL_STATUS')
      slots = tuple(dictStatus.getSlotsList().values_list("id", "title"))
      personal_status  = forms.ChoiceField(required=True, widget=forms.RadioSelect, choices=slots)

      site_name = forms.CharField(required=False, label=_("Site name"))
      site_name.widget.attrs.update({'class': 'text'})

      icq = forms.CharField(required=False, label=_("Icq"))
      icq.widget.attrs.update({'class': 'text'})

      skype = forms.CharField(required=False, label=_("Skype"))
      skype.widget.attrs.update({'class': 'text'})

      birthday = forms.DateField(required=False, label=_("Birthday"))
      birthday.widget.attrs.update({'class': 'date'})



      telephone_number = forms.CharField(required=False, label=_("Telephone"))
      telephone_number.widget.attrs.update({'class': 'text'})

      mobile_number = forms.CharField(required=False, label=_("Mobile number"))
      mobile_number.widget.attrs.update({'class': 'text'})

      profession = forms.CharField(required=False, label=_("Proffesion"))
      profession.widget.attrs.update({'class': 'text'})


      email = forms.EmailField(required=True)
      email.widget.attrs.update({'class': 'text'})



      def __init__(self,  *args, **kwargs):
         super(ProfileForm, self).__init__(*args, **kwargs)



