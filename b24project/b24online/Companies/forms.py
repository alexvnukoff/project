from django import forms
from django.contrib.contenttypes.forms import generic_inlineformset_factory

from b24online.models import AdditionalPage, Company, Country, Chamber


class CompanyForm(forms.ModelForm):
    vatin = forms.CharField(required=False)
    flag = forms.ImageField(required=False)
    phone = forms.CharField(required=True)
    fax = forms.CharField(required=False)
    site = forms.URLField(required=False)
    longitude = forms.DecimalField(required=True)
    latitude = forms.DecimalField(required=True)
    email = forms.EmailField(required=True)
    country = forms.ModelChoiceField(required=True, queryset=Country.objects.all())
    chamber = forms.ModelChoiceField(required=False, queryset=Chamber.objects.all())

    def __init__(self, *args, **kwargs):
        # first call parent's constructor
        super().__init__(*args, **kwargs)
        # there's a `fields` property now
        self.fields['logo'].required = True
        self.fields['director'].required = True
        self.fields['short_description'].required = True
        self.fields['address'].required = True

        if self.instance.pk:
            latitude, longitude = None, None

            if self.instance.location:
                latitude, longitude = self.instance.location.split(',')

            self.initial['phone'] = self.instance.phone
            self.initial['fax'] = self.instance.fax
            self.initial['site'] = self.instance.site
            self.initial['latitude'] = latitude
            self.initial['longitude'] = longitude
            self.initial['email'] = self.instance.email
            self.initial['vatin'] = self.instance.vatin
            self.initial['country'] = self.instance.country
            self.initial['chamber'] = self.instance.parent

    class Meta:
        model = Company
        fields = ('name', 'description', 'keywords', 'short_description', 'logo',
                  'director', 'address', 'slogan', 'branches', 'company_paypal_account')


AdditionalPageFormSet = generic_inlineformset_factory(AdditionalPage, fields=('title', 'content'), max_num=5,
                                                      validate_max=True, extra=0)
