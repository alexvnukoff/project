# -*- encoding: utf-8 -*-

import logging

from django import forms
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.forms import formset_factory

from b24online import InvalidParametersError
from b24online.models import (Questionnaire, Question, Answer, B2BProduct,
                              Recommendation)
from centerpokupok.models import B2CProduct

logger = logging.getLogger(__name__)


class QuestionnaireForm(forms.ModelForm):

    item_label = _('Questionnaire for')

    class Meta:
        model = Questionnaire
        fields = ['name', 'short_description', 'description', 
                  'red_level', 'yellow_level', 'green_level',
                  'image', 'use_show_result']

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

    def save(self, *args, **kwargs):
        if self.instance.pk:
            self.instance.updated_by = self.request.user
        else:
            self.instance.content_type = self._content_type
            self.instance.item = self.item
            self.instance.created_by = self.request.user
        return super(QuestionnaireForm, self).save(*args, **kwargs)


class QuestionForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = ['question_text',]

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

    def save(self, *args, **kwargs):
        if self.instance.pk:
            self.instance.updated_by = self.request.user
        else:
            self.instance.questionnaire = self.item
            self.instance.created_by = self.request.user
        return super(QuestionForm, self).save(*args, **kwargs)


class RecommendationForm(forms.ModelForm):

    class Meta:
        model = Recommendation
        fields = ['question', 'name', 'description', 'for_color']

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
        self.fields['question'].queryset = Question.objects\
            .filter(questionnaire=self.item)
        #self.fields['question'].required = True
        self.fields['description'].required = True

    def save(self, *args, **kwargs):
        if self.instance.pk:
            self.instance.updated_by = self.request.user
        else:
            self.instance.questionnaire = self.item
            self.instance.created_by = self.request.user
        return super(RecommendationForm, self).save(*args, **kwargs)


class ExtraQuestionForm(forms.Form):

    question_id = forms.IntegerField(
        label=_('Question ID'),
        widget=forms.HiddenInput,
        required=False,
    )
    approve = forms.BooleanField(
        label=_('Your answer'),
        required=False
    )

    def __init__(self, *args, **kwargs):
        data = kwargs.get('initial')
        if data and 'question' in data:
            self.question = data.pop('question')
        else:
            self.question = None
        super(ExtraQuestionForm, self).__init__(*args, **kwargs)

    def save(self):
        pass


class ExtraQuestionsForm(forms.Form):

    def __init__(self, request, questionnaire, *args, **kwargs):
        super(ExtraQuestionsForm, self).__init__(*args, **kwargs)
        self.request = request
        self.questionnaire = questionnaire

        params = {
            'initial': [{'question_id': question.id, 'question': question} \
                for question in self.questionnaire.get_extra_questions()]
            }
        if self.data:
            params.update({'data': self.data})

        self.formset = formset_factory(
            ExtraQuestionForm,
            extra=0,
            max_num=0,
            can_delete=True
        )(**params)

    def is_valid(self):
        if not super(ExtraQuestionsForm, self).is_valid():
            return False
        for item_form in self.formset:
            if not  item_form.is_valid():
                return False
        return True
        
    def save(self):
        for item_form in self.formset:
            on_delete, on_approve, question_id = map(
                lambda x: item_form.cleaned_data.get(x),
                ('DELETE', 'approve', 'question_id')
            )
            try:
                question = Question.objects.get(pk=question_id)
            except Question.DoesNotExist:
                continue
            else:
                if on_delete:
                    question.is_active = False
                elif on_approve:
                    question.approve = True
                question.save()
