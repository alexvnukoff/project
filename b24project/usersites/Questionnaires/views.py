# -*- encoding: utf-8 -*-

"""
The views for Questionnaires, Questions etc
"""

import logging

from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.generic import TemplateView

from b24online.models import (Questionnaire, QuestionnaireCase, Answer)
from guardian.mixins import LoginRequiredMixin
from b24online.cbv import ItemDetail
from usersites.mixins import UserTemplateMixin
from usersites.Questionnaires.forms import InviteForm

logger = logging.getLogger(__name__)
        

class QuestionnaireDetail(UserTemplateMixin, ItemDetail):
    model = Questionnaire
    template_name = '{template_path}/Questionnaires/detail.html'

    def get_object(self, queryset=None):
        self.case_uuid = self.kwargs.get('uuid', None)
        if self.case_uuid:
            try:
                self.case = QuestionnaireCase.objects.get(
                    case_uuid=self.case_uuid
                )
                return self.case.questionnaire
            except ObjectDoesNotExist:
                raise Http404(_('There is no such Questionnaire'))
        else:
            self.case = None
            return super(QuestionnaireDetail, self).get_object(
                queryset=queryset
            )

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = InviteForm(
            self.request, 
            self.object, 
            instance=self.case
        )
        return self.render_to_response(
            self.get_context_data(form=form, *args, **kwargs)
        )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = InviteForm(
            self.request,
            self.object,
            instance=self.case,    
            data=self.request.POST
        )
        logger.debug('Step 1')
        if form.is_valid():
            q_case = form.save()
            if q_case.case_uuid:
                success_url = reverse(
                    'questionnaires:ready', 
                    kwargs={'uuid': q_case.case_uuid})
                return HttpResponseRedirect(success_url)
            else:
                raise Http404(_('Unfortunately Your answers have'
                                ' not been registered'))
        return self.render_to_response(
            self.get_context_data(form=form, *args, **kwargs)
        )


class QuestionnaireReady(UserTemplateMixin, TemplateView):
    template_name = '{template_path}/Questionnaires/ready.html'

    def get(self, request, *args, **kwargs):
        case_uuid = kwargs.get('uuid')
        if case_uuid:
            try:
                self.case = QuestionnaireCase.objects.get(case_uuid=case_uuid)
            except QuestionnaireCase.DoesNotExist:
                pass
            else:
                if self.case.status == QuestionnaireCase.DRAFT:
                    self.case.status = QuestionnaireCase.READY
                    self.case.save()
                else:
                    kwargs['already'] = True
                kwargs.update({
                    'object': self.case.questionnaire,
                    'case': self.case,
                })
                return self.render_to_response(
                    self.get_context_data(*args, **kwargs)
                )
        raise Http404(_('There is no such Questionnaire'))
    

class QuestionnaireActivate(UserTemplateMixin, TemplateView):
    template_name = '{template_path}/Questionnaires/active.html'
        
    def get(self, request, *args, **kwargs):
        case_uuid = kwargs.get('uuid')
        if case_uuid:
            try:
                self.case = QuestionnaireCase.objects.get(case_uuid=case_uuid)
            except QuestionnaireCase.DoesNotExist:
                pass
            else:
                if self.case.status == QuestionnaireCase.READY:
                    self.case.status = QuestionnaireCase.ACTIVE
                    self.case.save()
                    return HttpResponseRedirect(
                        reverse(
                            'questionnaires:invited_answers',
                            kwargs={'uuid': case_uuid},
                        )
                    )
                kwargs.update({
                    'object': self.case.questionnaire,
                    'case': self.case,
                    'already': True,
                })
                return self.render_to_response(
                    self.get_context_data(*args, **kwargs)
                )
        raise Http404(_('There is no such Questionnaire'))


class QuestionnaireResults(UserTemplateMixin, TemplateView):
    template_name = '{template_path}/Questionnaires/results.html'

    # FIXME: divide on get_context_data and get by itself
    def get(self, request, *args, **kwargs):
        
        participant_type = kwargs.get('participant')
        case_uuid = kwargs.get('uuid')
        if case_uuid:
            try:
                self.case = QuestionnaireCase.objects.get(case_uuid=case_uuid)
            except QuestionnaireCase.DoesNotExist:
                pass
            else:
                if self.case.status == QuestionnaireCase.ACTIVE:
                    self.case.status = QuestionnaireCase.FINISHED
                    self.case.save()
                    
                kwargs.update({
                    'object': self.case.questionnaire,
                    'case': self.case,
                })

                participants = list(self.case.participants\
                    .order_by('is_invited'))
                is_correct = True
                logger.debug(participants)
                if len(participants) == 2:
                    inviter, invited = participants
                    if inviter.is_invited or not invited.is_invited:
                        is_correct = False
                    
                else:
                    is_correct = False
                if not is_correct:
                    raise Http404(_('There are some errors in'
                                    ' Questionnaire Case'))                
                if participant_type == 'inviter':
                    iam_inviter = True
                elif participant_type == 'invited':
                    iam_inviter = False

                answers = {}
                for answer in Answer.objects.filter(
                    questionnaire_case=self.case):
                    if not answer.question:
                        continue
                    logger.debug(answer.id)
                    logger.debug(answer.question.id)
                    logger.debug(answer.participant)
                    answers.setdefault(
                        answer.question.id, {})[answer.participant.pk] = answer
                    
                q_items = []
                for question in self.case.questionnaire.questions.all():
                    q_item = {'question': question,}
                    if iam_inviter:
                        answer = answers.get(question.id, {}).get(inviter.id)                    
                    else:
                        answer = answers.get(question.id, {}).get(invited.id)                    
                    q_item.update({'your': answer})
                    if iam_inviter:
                        answer = answers.get(question.id, {}).get(invited.id)                    
                    else:
                        answer = answers.get(question.id, {}).get(inviter.id)                    
                    q_item.update({'partner': answer})
                        
                    logger.debug(q_item)
                    q_items.append(q_items)
                kwargs.update({
                    'inviter': inviter,
                    'invited': invited,
                    'q_items': q_items,
                })
                return self.render_to_response(
                    self.get_context_data(*args, **kwargs)
                )
        raise Http404(_('There is no such Questionnaire'))

