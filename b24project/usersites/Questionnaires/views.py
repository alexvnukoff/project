# -*- encoding: utf-8 -*-

"""
The views for Questionnaires, Questions etc
"""

import uuid
import logging

from django.conf import settings
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.generic import TemplateView
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from b24online.models import (Questionnaire, QuestionnaireCase, Answer)
from guardian.mixins import LoginRequiredMixin
from b24online.cbv import ItemDetail, ItemsList
from usersites.mixins import UserTemplateMixin
from usersites.Questionnaires.forms import InviteForm, HistoryForm
from tpp.DynamicSiteMiddleware import get_current_site

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
        if form.is_valid():
            q_case = form.save()
            if q_case.case_uuid:
                if form.is_invited:
                    domain = get_current_site().domain
                    next_url = 'http://{0}{1}' . format(
                        domain,
                        reverse('questionnaires:results',
                                kwargs={'uuid': q_case.case_uuid,
                                        'participant': 'inviter'})
                    )
                    result_href = '<a href="{0}">{1}</a>' . format(
                        next_url,
                        _('Results')
                    )
                   
                    inviter = q_case.get_inviter()
                    if inviter and inviter.email:
                        results_subject = _('The questionnaire started by '
                                    'You has beed finished')
                        results_message = render_to_string(
                            'usersites/Questionnaires/resultsEmail.txt',
                            {'q_case': q_case, 'result_href': result_href}
                        )
                        results_mail = EmailMessage(
                            results_subject, 
                            results_message,
                            settings.DEFAULT_FROM_EMAIL, 
                            [inviter.email,]
                        )
                        report_subject = _('The questionnaire created by '
                                    'You has been finished')
                        report_message = render_to_string(
                            'usersites/Questionnaires/reportEmail.txt',
                            {'q_case': q_case}
                        )
                        report_mail = EmailMessage(
                            report_subject, 
                            report_message,
                            settings.DEFAULT_FROM_EMAIL,
                            [q_case.questionnaire.created_by.email,], 
                        )
                        if not getattr(settings, 'NOT_SEND_EMAIL', False):
                            results_mail.send()

                    form.process_answers()
                    success_url = reverse(
                        'questionnaires:results',
                        kwargs={
                            'uuid': q_case.case_uuid,
                            'participant': 'invited',
                        }
                    )
                else:
                    domain = get_current_site().domain
                    next_url = 'http://{0}{1}' . format(
                        domain,
                        reverse('questionnaires:activate',
                                kwargs={'uuid': q_case.case_uuid,})
                    )          
                    result_href = '<a href="{0}">{1}</a>' . format(
                        next_url,
                        _('Answer the questions')
                    )
                    invited = q_case.get_invited()
                    if invited and invited.email:
                        subject = _('Invite to answer the questions')
                        message = render_to_string(
                            'usersites/Questionnaires/resultsInviterEmail.txt',
                            {'q_case': q_case, 'inviter': inviter, 
                             'result_href': result_href}
                        )
                        mail = EmailMessage(
                            subject, 
                            message,
                            settings.DEFAULT_FROM_EMAIL, 
                            [invited.email,]
                        )
                        if not getattr(settings, 'NOT_SEND_EMAIL', False):
                            mail.send()

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

                data = list(self.case.get_coincedences())
                coincedences = len([item for item in data \
                    if item.get('is_coincedence')])

                q_colors = sorted((
                    (['red', 'grey', 'grey'],
                     self.case.questionnaire.red_level),
                    (['grey', 'yellow',' grey'],
                     self.case.questionnaire.yellow_level),
                    (['grey', 'grey', 'green'],
                     self.case.questionnaire.green_level),
                ), key=lambda x: x[1], reverse=True)

                colors = ['grey', 'grey', 'grey']
                for (_colors, hm) in q_colors:
                    if coincedences > hm or (hm == 0 and coincedences >= hm):
                        colors = _colors
                        break

                if self.case.questionnaire.use_show_result:
                    q_items = [q_item for q_item in data \
                        if q_item.get('need_show')]
                else:
                    q_items = [q_item for q_item in data \
                        if q_item.get('is_coincedence')]
                kwargs.update({
                    'object': self.case.questionnaire,
                    'case': self.case,
                    'q_items': q_items,
                    'q_colors': colors,
                })

                return self.render_to_response(
                    self.get_context_data(*args, **kwargs)
                )
        raise Http404(_('There is no such Questionnaire'))


class QuestionnaireCaseList(UserTemplateMixin, TemplateView):
    """
    The Questionnaire list view.
    """
    model = QuestionnaireCase
    template_name = '{template_path}/Questionnaires/contentPage.html'

    def get(self, request, *args, **kwargs):
        self.email = None
        if request.user.is_authenticated():
            self.email = request.user.email
        else:
            history_uuid = kwargs.get('uuid')
            if history_uuid:
                history_info = request.session.get('history_info')
                if history_info:
                    self.email = history_info.get(history_uuid)
        if self.email:
            return super().get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('denied'))


class QuestionnaireCaseHistory(UserTemplateMixin, TemplateView):
    """
    The Questionnaire history form view.
    """
    model = QuestionnaireCase
    template_name = '{template_path}/Questionnaires/history.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            self.email = request.user.email
            self.template_name = '{template_path}/Questionnaires/contentPage.html'
            return self.render_to_response(
                self.get_context_data(*args, **kwargs)
            )
        else:
            form = HistoryForm()
            return self.render_to_response(
                self.get_context_data(form=form, *args, **kwargs)
            )

    def post(self, request, *args, **kwargs):
        form = HistoryForm(
            data=self.request.POST
        )
        self.email = None
        if form.is_valid():
            self.email = form.cleaned_data.get('email')
            history_uuid = str(uuid.uuid4())
            request.session['history_info'] = {history_uuid: self.email}
            domain = get_current_site().domain
            history_url = 'http://{0}{1}' . format(
                domain,
                reverse('questionnaires:case_list',
                        kwargs={'uuid': history_uuid}))

            subject = _('The request about Questionnaires history')
            message = render_to_string(
                        'usersites/Questionnaires/historyEmail.txt',
                        {'history_url': history_url}
                    )
            smail = EmailMessage(
                subject, 
                message,
                settings.DEFAULT_FROM_EMAIL,
                [self.email,], 
            )
            if not getattr(settings, 'NOT_SEND_EMAIL', False):
                smail.send()
        return self.render_to_response(
            self.get_context_data(form=form, *args, **kwargs)
        )
