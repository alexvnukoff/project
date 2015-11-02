from django import forms

from b24online.models import Vacancy
from jobs.models import Requirement


class VacancyChoiceField(forms.ModelChoiceField):

    def optgroup_from_instance(self, obj):
        return obj.department.name

    def __choice_from_instance__(self, obj):
        return (obj.id, self.label_from_instance(obj))

    def _get_choices(self):
        if not self.queryset:
            return []

        all_choices = []
        if self.empty_label:
            current_optgroup = ""
            current_optgroup_choices = [("", self.empty_label)]
        else:
            current_optgroup = self.optgroup_from_instance(self.queryset[0])
            current_optgroup_choices = []

        for item in self.queryset:
            optgroup_from_instance = self.optgroup_from_instance(item)
            if current_optgroup != optgroup_from_instance:
                all_choices.append((current_optgroup, current_optgroup_choices))
                current_optgroup_choices = []
                current_optgroup = optgroup_from_instance
            current_optgroup_choices.append(self.__choice_from_instance__(item))

        all_choices.append((current_optgroup, current_optgroup_choices))

        return all_choices

    choices = property(_get_choices, forms.ChoiceField._set_choices)


class RequirementForm(forms.ModelForm):
    vacancy = VacancyChoiceField(required=True, queryset=Vacancy.objects.none())

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        self.fields["vacancy"].queryset = Vacancy.objects \
            .filter(department__organization=request.session.get('current_company')) \
            .select_related('department').order_by('department__name', 'name')

        if self.instance.pk:
            self.initial['vacancy'] = self.instance.vacancy

    class Meta:
        model = Requirement
        fields = ('title', 'description', 'keywords', 'city', 'type_of_employment',
                  'requirements', 'terms', 'is_anonymous', 'country')
