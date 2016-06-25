from django import forms
from django.contrib.contenttypes.forms import generic_inlineformset_factory
from b24online.models import InnovationProject, AdditionalPage


class InnovationProjectForm(forms.ModelForm):
    site = forms.URLField()
    release_date = forms.DateField(input_formats=["%d/%m/%Y"])

    def __init__(self, *args, **kwargs):
        # first call parent's constructor
        super().__init__(*args, **kwargs)
        # there's a `fields` property now
        self.fields['cost'].required = True
        self.fields['currency'].required = True

        if self.instance.pk:
            self.initial['site'] = self.instance.site
            self.initial['release_date'] = self.instance.release_date

    class Meta:
        model = InnovationProject
        fields = ('name', 'description', 'keywords', 'product_name', 'currency', 'cost',
                  'business_plan', 'branches', 'product_name')

AdditionalPageFormSet = generic_inlineformset_factory(AdditionalPage, fields=('title', 'content'), max_num=5,
                                                      validate_max=True, extra=0)
