from django import forms
from django.contrib.contenttypes.forms import generic_inlineformset_factory

from b24online.models import AdditionalPage, Chamber


class ChamberForm(forms.ModelForm):
    flag = forms.ImageField(required=False)
    phone = forms.CharField(required=False)
    fax = forms.CharField(required=False)
    site = forms.URLField(required=False)
    location = forms.CharField(required=False)
    email = forms.EmailField(required=False)

    def __init__(self, *args, **kwargs):
        # first call parent's constructor
        super().__init__(*args, **kwargs)
        # there's a `fields` property now
        self.fields['logo'].required = True

        if self.instance:
            self.initial['flag'] = self.instance.flag
            self.initial['phone'] = self.instance.phone
            self.initial['fax'] = self.instance.fax
            self.initial['site'] = self.instance.site
            self.initial['location'] = self.instance.location
            self.initial['email'] = self.instance.email


    class Meta:
        model = Chamber
        fields = ('name', 'description', 'keywords', 'short_description', 'logo',
                  'director', 'address', 'org_type', 'countries')


AdditionalPageFormSet = generic_inlineformset_factory(AdditionalPage, fields=('title', 'content'), max_num=5,
                                                      validate_max=True, extra=1)
