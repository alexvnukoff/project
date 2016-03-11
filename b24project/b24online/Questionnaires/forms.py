# -*- encoding: utf-8 -*-

import logging

from django import forms
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.conf import settings

from b24online.models import (Questionnaire, Question, Answer)


class QuestionnaireForm(forms.ModelForm):

    class Meta:
        model = Questionnaire
        fields = ('name',)

    