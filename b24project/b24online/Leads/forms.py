# -*- coding: utf-8 -*-
from django import forms
from b24online.models import LeadsStore


class LeadEditForm(forms.ModelForm):
    class Meta:
        model = LeadsStore
        fields = ('realname', 'email', 'phone', 'message')

