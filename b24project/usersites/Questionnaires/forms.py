# -*- encoding: utf-8 -*-

import logging

from django import forms
from django.utils.translation import gettext as _
from django.conf import settings
from django.forms import formset_factory

from b24online import InvalidParametersError
from b24online.models import (Questionnaire, Question, Answer, B2BProduct,
                              Recommendation)

logger = logging.getLogger(__name__)


class AnswerForm(forms.Form):
    
    ANSWER_YES, ANSWER_NO = 'yes', 'no'
    ANSWERS = (
        (ANSWER_YES, _('Yes')),
        (ANSWER_NO, _('No')),
    )
    
    question_id = forms.IntegerField(
        label=_('Question ID'),
        widget=forms.HiddenInput, 
    )
    question_text = forms.CharField(
        label=_('Your answer'),
        required=False,
        widget=forms.Textarea(attrs={'rows': '2', 'cols': '40'}),
    )
    agree = forms.ChoiceField(
        label=_('Your answer'),
        choices=ANSWERS,
        required=True,
        widget=forms.RadioSelect,
    )

    def __init__(self, *args, **kwargs):
        data = kwargs.get('initial')
        if data and 'question' in data:
            self.question = data.pop('question')
        else:
            self.question = None
        super(AnswerForm, self).__init__(*args, **kwargs)
        self.initial['agree'] = self.ANSWER_YES
        
    def save(self):
        pass


AnswerFormset = formset_factory(AnswerForm, extra=1, max_num=10)


class InviteForm(forms.Form):
    
    invite_by_email = forms.EmailField(
        label=_('Invite User by Email'),
        widget=forms.TextInput(attrs={'size': 60})
    )
    
    def __init__(self, questionnaire, *args, **kwargs):
        super(InviteForm, self).__init__(*args, **kwargs)
        self.questionnaire = questionnaire
        initial = []
        for question in self.questionnaire.questions.all():
            initial.append({'question_id': question.id, 'question': question})
        self.answer_formset = AnswerFormset(initial=initial)
