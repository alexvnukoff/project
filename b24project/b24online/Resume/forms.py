from django import forms
from django.forms import formset_factory
from django.utils.translation import gettext as _

from jobs.models import Resume


class WorkPositionForm(forms.Form):
    company_name = forms.CharField(required=True)
    position = forms.CharField(required=True)
    start_work = forms.DateField(required=True, input_formats=["%d/%m/%Y"])
    end_work = forms.DateField(required=False, input_formats=["%d/%m/%Y"])

    def clean(self):
        cleaned_data = super().clean()
        start_work = cleaned_data.get("start_work")
        end_work = cleaned_data.get("end_work")

        if start_work and end_work and start_work >= end_work:
            self.add_error('study_start_date', _('Starting date should be earlier than ending date'))


class ResumeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        # first call parent's constructor
        super().__init__(*args, **kwargs)
        # there's a `fields` property now
        self.fields['study_start_date'].input_formats = ["%d/%m/%Y"]
        self.fields['study_end_date'].input_formats = ["%d/%m/%Y"]

    def clean(self):
        cleaned_data = super().clean()
        study_start_date = cleaned_data.get("study_start_date")
        study_end_date = cleaned_data.get("study_end_date")

        if study_start_date and study_end_date and study_start_date >= study_end_date:
            self.add_error('study_start_date', _('Starting date should be earlier than ending date'))

    class Meta:
        model = Resume
        fields = ('title', 'martial_status', 'nationality', 'telephone_number', 'address', 'faculty', 'profession',
                  'study_start_date', 'study_end_date', 'study_form', 'additional_study', 'language_skill',
                  'computer_skill', 'additional_skill', 'salary', 'additional_information', 'institution')


WorkPositionFormSet = formset_factory(WorkPositionForm, extra=3, max_num=3, min_num=0)