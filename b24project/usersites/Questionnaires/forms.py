# -*- encoding: utf-8 -*-

import logging

from django.core.exceptions import ValidationError
from django.http import Http404
from django.db import transaction, IntegrityError
from django import forms
from django.utils.translation import gettext as _
from django.conf import settings
from django.forms import formset_factory

from b24online import InvalidParametersError
from b24online.models import (User, Questionnaire, QuestionnaireCase,
                              QuestionnaireParticipant, Question, Answer)

logger = logging.getLogger(__name__)


class AnswerForm(forms.Form):
    
    question_id = forms.IntegerField(
        label=_('Question ID'),
        widget=forms.HiddenInput, 
        required=False,
    )
    question_text = forms.CharField(
        label=_('Your answer'),
        required=False,
        widget=forms.Textarea(attrs={'rows': '2', 'cols': '40'}),
    )
    agree = forms.BooleanField(
        label=_('Your answer'),
        required=False
    )

    def __init__(self, *args, **kwargs):
        data = kwargs.get('initial')
        if data and 'question' in data:
            self.question = data.pop('question')
        else:
            self.question = None
        super(AnswerForm, self).__init__(*args, **kwargs)
        
    def save(self):
        pass


AnswerFormset = formset_factory(AnswerForm, extra=1, max_num=30)


class InviteForm(forms.Form):
    
    inviter_email = forms.EmailField(
        label=_('Your Email'),
        widget=forms.TextInput(attrs={'size': 60}),
        required=True,
    )
    
    invite_by_email = forms.EmailField(
        label=_('Invite User by Email'),
        widget=forms.TextInput(attrs={'size': 60}),
        required=True,
    )
    
    def __init__(self, request, questionnaire, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        self.is_invited = True if self.instance else False
        super(InviteForm, self).__init__(*args, **kwargs)
        self.request = request
        if self.instance:
            del self.fields['inviter_email']
            del self.fields['invite_by_email']
        self.questionnaire = questionnaire
        params = {
            'initial': [{'question_id': question.id, 'question': question} \
                for question in self.questionnaire.questions.all()]
        }
        if self.data:
            params.update({'data': self.data})
        self.answer_formset = AnswerFormset(**params)

    def is_valid(self):
        it_is_valid = super(InviteForm, self).is_valid()
        for q_form in self.answer_formset:
            it_is_valid = it_is_valid and q_form.is_valid()
        return it_is_valid

    def save(self):
        try:
            with transaction.atomic():
                if not self.instance:
                    self.instance = QuestionnaireCase.objects.create(
                        questionnaire=self.questionnaire,
                        status=QuestionnaireCase.DRAFT,
                    )
                if self.is_invited:
                    try:
                        responsive = self.instance.participants.filter(
                            is_invited=True
                        )[0]
                    except IndexError:
                        raise Http404(_('There is no suitable participant'))
                        
                else:
                    invite_by_email = self.cleaned_data\
                        .get('invite_by_email')
                    if invite_by_email:
                        invited_participant = QuestionnaireParticipant.objects\
                            .create(
                                email=invite_by_email,
                                is_invited=True
                            )
                        self.instance.participants.add(invited_participant)
                    inviter_email = self.cleaned_data.get('inviter_email')
                    if inviter_email:
                        inviter_participant = QuestionnaireParticipant(
                            email=inviter_email,
                            is_invited=False,
                        )
                        if self.request.user.is_authenticated():
                            inviter_participant.user = self.request.user
                        inviter_participant.save()
                        self.instance.participants.add(inviter_participant)
                        responsive = inviter_participant

                for q_form in self.answer_formset:
                    if 'agree' in q_form.cleaned_data and \
                        q_form.cleaned_data['agree']:
                        new_answer = Answer.objects.create(
                            questionnaire_case=self.instance,
                            question=q_form.question,
                            participant=responsive,
                            answer=True
                        )                                            
        except IntegrityError:
            raise
        else:          
            return self.instance


    def process_answers(self):
        existed_ids = [r.id for r in self.case.recommendations.all()]                
        for item in self.case.get_coincedences():
            if item.get('is_coincedence'):
                question = item.get('question')
                for r_item in Recommendation.objects.filter(
                    question=question):
                    if r_item not in existed_ids:
                        qc.recommendations.add(r_item)
        
        