from django import forms
from django.contrib.contenttypes.forms import generic_inlineformset_factory

from b24online.models import AdditionalPage, BusinessProposal


class BusinessProposalForm(forms.ModelForm):

    class Meta:
        model = BusinessProposal
        fields = ('title', 'description', 'keywords', 'categories', 'country', 'branches')

AdditionalPageFormSet = generic_inlineformset_factory(AdditionalPage, fields=('title', 'content'), max_num=5,
                                                      validate_max=True, extra=0)
