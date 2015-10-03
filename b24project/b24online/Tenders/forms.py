from django import forms
from django.contrib.contenttypes.forms import generic_inlineformset_factory
from django.utils.translation import gettext as _

from b24online.models import AdditionalPage, Tender


class TenderForm(forms.ModelForm):
    start_date = forms.DateField(input_formats=["%d/%m/%Y"], required=True)
    end_date = forms.DateField(input_formats=["%d/%m/%Y"], required=True)

    def __init__(self, *args, **kwargs):
        # first call parent's constructor
        super().__init__(*args, **kwargs)

        if self.instance.pk and self.instance.start_date and self.instance.end_date:
            self.initial['start_date'] = self.instance.start_date.strftime('%d/%m/%Y')
            self.initial['end_date'] = self.instance.end_date.strftime('%d/%m/%Y')

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and start_date > end_date:
            self.add_error('start_date', _('Starting date should be earlier than ending date'))

    class Meta:
        model = Tender
        fields = ('title', 'content', 'keywords', 'currency', 'cost', 'country', 'branches')

AdditionalPageFormSet = generic_inlineformset_factory(AdditionalPage, fields=('title', 'content'), max_num=5,
                                                      validate_max=True, extra=0)
