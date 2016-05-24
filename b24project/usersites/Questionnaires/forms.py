# -*- encoding: utf-8 -*-

import logging

from django.core.exceptions import ValidationError
from django.http import Http404
from django.db import transaction, IntegrityError
from django.db.models import Q
from django import forms
from django.utils.translation import gettext as _
from django.conf import settings
from django.forms import formset_factory

from b24online import InvalidParametersError
from b24online.models import (User, Questionnaire, QuestionnaireCase,
                              QuestionnaireParticipant, Question, Answer,
                              Recommendation)

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
        widget=forms.Textarea(
            attrs={
                'rows': '3', 
                'placeholder': _('Ask Your own question'),
                'style': 'min-width: 150px; max-width: 350px; width: 200px;'
            }
        ),
    )
    agree = forms.BooleanField(
        label=_('Your answer'),
        required=False
    )
    show = forms.BooleanField(
        label=_('Show the answer'),
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


class InviteForm(forms.Form):

    inviter_email = forms.EmailField(
        label=_('Your Email'),
        widget=forms.TextInput(
            attrs={'style': 'min-width: 150px; max-width: 350px; width: 250px;'}
        ),
        required=True,
    )

    invite_by_email = forms.EmailField(
        label=_('Invite User by Email'),
        widget=forms.TextInput(
            attrs={'style': 'min-width: 150px; max-width: 350px; width: 250px;'}
        ),
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
        elif self.request.user.is_authenticated():
            self.fields['inviter_email'].widget = forms.HiddenInput()
            self.hidden_fields['inviter_email'] = self.fields['inviter_email']
        self.questionnaire = questionnaire
        if self.is_invited:
            extra_ids = [q.id for q in self.instance.extra_questions.all()]
            params = {
                'initial': [{'question_id': question.id, 'question': question} \
                for question in self.questionnaire.questions\
                    .filter((Q(who_created=Question.BY_AUTHOR) | \
                             Q(id__in=extra_ids)),
                            is_active=True, is_deleted=False,)]
            }
        else:
            params = {
                'initial': [{'question_id': question.id, 'question': question} \
                for question in self.questionnaire.questions\
                    .filter((Q(who_created=Question.BY_AUTHOR) | \
                             Q(is_approved=True)),
                            is_active=True, is_deleted=False)]
            }
        if self.data:
            params.update({'data': self.data})

        extra = 0 if self.is_invited else 1
        self.answer_formset = formset_factory(
            AnswerForm,
            extra=extra,
            max_num=100
        )(**params)

    def is_valid(self):
        it_is_valid = super(InviteForm, self).is_valid()
        for q_form in self.answer_formset:
            it_is_valid = it_is_valid and q_form.is_valid()
        return it_is_valid

    def save(self):
        inviter_participant = None
        try:
            with transaction.atomic():
                if not self.instance:
                    self.instance = QuestionnaireCase.objects.create(
                        questionnaire=self.questionnaire,
                        status=QuestionnaireCase.DRAFT,
                    )
                if self.is_invited:
                    try:
                        responsive = self.instance.participants.get(
                            is_invited=True
                        )
                    except QuestionnaireParticipant.DoesNotExist:
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
                    if not q_form.question and inviter_participant:
                        if 'question_text' not in q_form.cleaned_data:
                            continue
                        question = Question.objects.create(
                            questionnaire=self.questionnaire,
                            who_created=Question.BY_MEMBER,
                            created_by_participant=inviter_participant,
                            question_text=q_form.cleaned_data['question_text']
                        )
                        self.instance.extra_questions.add(question)
                    else:
                        question = q_form.question

                    new_answer = Answer.objects.create(
                        questionnaire_case=self.instance,
                        question=question,
                        participant=responsive,
                        answer=q_form.cleaned_data.get('agree', False),
                        show_answer=q_form.cleaned_data.get('show', False) \
                            if self.questionnaire.use_show_result else False,
                        )

        except IntegrityError:
            raise
        else:
            return self.instance

    def process_answers(self):
        data = list(self.instance.get_coincedences())
        coincedences = len([item for item in data \
            if item.get('is_coincedence')])
        q_colors = sorted((
            ('red', self.questionnaire.red_level),
            ('yellow', self.questionnaire.yellow_level),
            ('green', self.questionnaire.green_level)
        ), key=lambda x: x[1], reverse=True)

        color = None
        for (_color, hm) in q_colors:
            if coincedences > hm or (hm == 0 and coincedences >= hm):
                color = _color
                break

        existed_ids = [r.id for r in self.instance.recommendations.all()]
        
        items = [item['question'].pk for item in \
                list(self.instance.get_coincedences()) \
                    if item.get('is_coincedence') and 'question' in item]
        question_ids = filter(lambda x: x not in existed_ids, items)
        ritems = Recommendation.objects.filter(
            Q(questionnaire=self.questionnaire) & (
            Q(question__id__in=question_ids) | \
            Q(for_color=color))
        )
        self.instance.recommendations.add(*ritems)


class HistoryForm(forms.Form):

    email = forms.EmailField(
        label=_('Email'),
        required=True,
        widget=forms.TextInput(
            attrs={
                'style': 'min-width: 150px; max-width: 350px; width: 200px;'
            }
        ),
    )
