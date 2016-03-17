# -*- encoding: utf-8 -*-

import logging

from django import forms
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from b24online import InvalidParametersError
from b24online.models import (Questionnaire, Question, Answer, B2BProduct,
                              Recommendation)
from centerpokupok.models import B2CProduct

logger = logging.getLogger(__name__)


class QuestionnaireForm(forms.ModelForm):

    item_label = _('Questionnaire for')

    class Meta:
        model = Questionnaire
        fields = ['name', 'short_description', 'description', 'image']

    def __init__(self, request, content_type_id=None, item_id=None, 
                 *args, **kwargs):
        cls = type(self)
        super(QuestionnaireForm, self).__init__(*args, **kwargs)
        self.request = request
        if self.instance and self.instance.pk:
            self.item = self.instance.item
        else:
            try:
                self._content_type = ContentType.objects.get(
                    pk=content_type_id
                )
            except ContentType.DoesNotExist:
                raise InvalidParametersError(
                    _('Invalid ContentType ID')
                )
            else:
                model_class = self._content_type.model_class()
                try:
                    self.item = model_class.objects.get(pk=item_id)
                except model_class.DoesNotExist:
                    raise InvalidParametersError(
                        _('Invalid Object ID')
                    )

    def save(self, commit=True):
        instance = super(QuestionnaireForm, self).save(commit=False)
        if instance.pk:
            instance.updated_by = self.request.user
        else:
            instance.content_type = self._content_type
            instance.item = self.item
            instance.created_by = self.request.user
        if commit:
            instance.save()
        return instance


class QuestionForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = ['question_text', 'score_positive', 'score_negative']

    def __init__(self, request, item_id=None, *args, **kwargs):
        cls = type(self)
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.request = request
        if self.instance and self.instance.pk:
            self.item = self.instance.questionnaire
        else:
            try:
                self.item = Questionnaire.objects.get(pk=item_id)
            except Questionnaire.DoesNotExist:
                raise InvalidParametersError(
                    _('Invalid Object ID')
                )

    def save(self, commit=True):
        instance = super(QuestionForm, self).save(commit=False)
        if instance.pk:
            instance.updated_by = self.request.user
        else:
            instance.questionnaire = self.item
            instance.created_by = self.request.user
        if commit:
            instance.save()
        return instance


class RecommendationForm(forms.ModelForm):

    class Meta:
        model = Recommendation
        fields = ['name', 'description', 'is_coincided', 'is_positive_answer']

    def __init__(self, request, item_id=None, *args, **kwargs):
        cls = type(self)
        super(RecommendationForm, self).__init__(*args, **kwargs)
        self.request = request
        if self.instance and self.instance.pk:
            self.item = self.instance.questionnaire
        else:
            try:
                self.item = Questionnaire.objects.get(pk=item_id)
            except Questionnaire.DoesNotExist:
                raise InvalidParametersError(
                    _('Invalid Object ID')
                )

    def save(self, commit=True):
        instance = super(RecommendationForm, self).save(commit=False)
        if instance.pk:
            instance.updated_by = self.request.user
        else:
            instance.questionnaire = self.item
            instance.created_by = self.request.user
        if commit:
            instance.save()
        return instance
