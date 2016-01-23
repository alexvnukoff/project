# -*- coding: utf-8 -*-
from django import forms
from usersites.models import UserSiteTemplate


class UserSiteTemplateForm(forms.ModelForm):
    class Meta:
        model = UserSiteTemplate
        fields = '__all__'