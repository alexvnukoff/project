# -*- encoding: utf-8 -*-

"""
The views for Questionnaires, Questions etc
"""

import logging

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import (HttpResponseRedirect, Http404,
                         HttpResponseBadRequest)
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from guardian.mixins import LoginRequiredMixin

from b24online.Questionnaires.forms import (
    QuestionnaireForm,
    QuestionForm,
    RecommendationForm,
    ExtraQuestionsForm,
)
from b24online.cbv import (ItemsList, ItemDetail, ItemUpdate, ItemCreate,
                           ItemDeactivate)
from b24online.models import (Company, B2BProduct, Questionnaire,
                              QuestionnaireCase, Question, Recommendation)
from b24online.utils import (get_by_content_type, get_permitted_orgs)
from centerpokupok.models import B2CProduct

logger = logging.getLogger(__name__)


def can_manage_product(user, item):
    """
    Return if the user can manage the product.
    """
    if isinstance(item, (B2BProduct, B2CProduct)) and item.id and item.company \
            and item.company in get_permitted_orgs(user, model_klass=Company):
        return True
    return False


class QuestionnaireCreate(LoginRequiredMixin, ItemCreate):
    """
    The view for creatting.
    """
    model = Questionnaire
    form_class = QuestionnaireForm
    template_name = 'b24online/Questionnaires/form.html'
    success_url = reverse_lazy('questionnaires:main')

    def dispatch(self, request, *args, **kwargs):
        self.object = None
        self.content_type_id = kwargs.pop('content_type_id')
        self.item_id = kwargs.pop('item_id')
        if not can_manage_product(request.user,
                                  get_by_content_type(self.content_type_id, self.item_id)):
            return HttpResponseRedirect(reverse('denied'))

        return super(QuestionnaireCreate, self) \
            .dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(
            request,
            content_type_id=self.content_type_id,
            item_id=self.item_id
        )
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        form = self.form_class(
            request,
            content_type_id=self.content_type_id,
            item_id=self.item_id,
            data=request.POST,
            files=request.FILES
        )
        if form.is_valid():
            form.save()
            if form.changed_data and 'image' in form.changed_data:
                form.instance.upload_image()
            success_url = reverse(
                'questionnaires:list',
                kwargs={
                    'content_type_id': self.content_type_id,
                    'item_id': self.item_id,
                })
            return HttpResponseRedirect(success_url)
        return self.render_to_response(self.get_context_data(form=form))


class QuestionnaireUpdate(LoginRequiredMixin, ItemUpdate):
    """
    The view for creating.
    """
    model = Questionnaire
    form_class = QuestionnaireForm
    template_name = 'b24online/Questionnaires/form.html'
    success_url = reverse_lazy('questionnaires:main')

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not can_manage_product(request.user, self.object.item):
            return HttpResponseRedirect(reverse('denied'))

        return super(QuestionnaireUpdate, self) \
            .dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(
            request,
            instance=self.object,
        )
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        form = self.form_class(
            request,
            instance=self.object,
            data=request.POST,
            files=request.FILES
        )
        if form.is_valid():
            form.save()
            if form.changed_data and 'image' in form.changed_data:
                form.instance.upload_image()
            success_url = reverse(
                'questionnaires:list',
                kwargs={
                    'content_type_id': self.object.content_type_id,
                    'item_id': self.object.object_id,
                })
            return HttpResponseRedirect(success_url)
        return self.render_to_response(self.get_context_data(form=form))


class QuestionnaireList(LoginRequiredMixin, ItemsList):
    """
    The Questionnaire list view.
    """
    model = Questionnaire
    template_name = 'b24online/Questionnaires/list.html'
    url_paginator = 'questionnaires:list_for_item_paginator'
    paginate_by = 10
    sortField1 = 'created_at'
    order1 = 'asc'

    def dispatch(self, request, *args, **kwargs):
        self.content_type_id = self.kwargs.get('content_type_id')
        self.product_id = self.kwargs.get('item_id')
        self.product = None
        if self.content_type_id and self.product_id:
            self.product = get_by_content_type(
                self.content_type_id,
                self.product_id
            )
            if not can_manage_product(request.user, self.product):
                return HttpResponseRedirect(reverse('denied'))

            if not self.product:
                raise Http404(_('There is no such instance'))

        return super(QuestionnaireList, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super(QuestionnaireList, self).get_queryset()
        if self.product:
            qs = qs.filter(
                content_type_id=self.content_type_id,
                object_id=self.product_id
            )
        return qs


class QuestionnaireDetail(ItemDetail):
    model = Questionnaire
    template_name = 'b24online/Questionnaires/detail.html'
    form_class = ExtraQuestionsForm

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not can_manage_product(request.user, self.object.item):
            return HttpResponseRedirect(reverse('denied'))
        return super(QuestionnaireDetail, self) \
            .dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(QuestionnaireDetail, self).get_context_data(**kwargs)
        questionnaire = context.get('item')
        self._product = questionnaire.item
        context.update({'product': self._product, 'can_manage': True})
        return context

    def get(self, request, *args, **kwargs):
        form = self.form_class(
            request,
            self.object,
        )
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        form = self.form_class(
            request,
            self.object,
            data=request.POST,
        )
        if form.is_valid():
            form.save()
            success_url = reverse(
                'questionnaires:detail',
                kwargs={'item_id': self.object.pk,
                        })
            return HttpResponseRedirect(success_url)
        return self.render_to_response(self.get_context_data(form=form))


class QuestionnaireDelete(ItemDeactivate):
    model = Questionnaire

    def get_success_url(self):
        return reverse(
            'questionnaires:list',
            kwargs={
                'content_type_id': self.object.content_type_id,
                'item_id': self.object.item.pk
            }
        )

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not can_manage_product(request.user, self.object.item):
            return HttpResponseRedirect(reverse('denied'))
        return super(QuestionnaireDelete, self) \
            .dispatch(request, *args, **kwargs)


class QuestionDelete(ItemDeactivate):
    model = Question

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not can_manage_product(request.user,
                                  self.object.questionnaire.item):
            return HttpResponseRedirect(reverse('denied'))
        return super(QuestionDelete, self) \
            .dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'questionnaires:detail',
            kwargs={'item_id': self.object.questionnaire.pk}
        )


class RecommendationDelete(ItemDeactivate):
    model = Recommendation

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not can_manage_product(request.user, self.object.questionnaire.item):
            return HttpResponseRedirect(reverse('denied'))
        return super(RecommendationDelete, self) \
            .dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'questionnaires:detail',
            kwargs={'item_id': self.object.questionnaire.pk}
        )


class QuestionCreate(LoginRequiredMixin, ItemCreate):
    """
    The view for creating.
    """
    model = Question
    form_class = QuestionForm
    template_name = 'b24online/Questionnaires/questionForm.html'
    success_url = reverse_lazy('questionnaires:main')

    def dispatch(self, request, *args, **kwargs):
        self.object = None
        self.item_id = kwargs.pop('item_id')
        try:
            _questionnaire = Questionnaire.objects.get(pk=self.item_id)
        except:
            return HttpResponseRedirect(reverse('denied'))
        else:
            if not can_manage_product(request.user, _questionnaire):
                return HttpResponseRedirect(reverse('denied'))

        return super(QuestionCreate, self) \
            .dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(
            request,
            item_id=self.item_id
        )
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        form = self.form_class(
            request,
            item_id=self.item_id,
            data=request.POST,
            files=request.FILES
        )
        if form.is_valid():
            form.save()
            success_url = reverse(
                'questionnaires:detail',
                kwargs={
                    'item_id': self.item_id,
                })
            return HttpResponseRedirect(success_url)
        return self.render_to_response(self.get_context_data(form=form))


class QuestionUpdate(LoginRequiredMixin, ItemUpdate):
    """
    The view for creating.
    """
    model = Question
    form_class = QuestionForm
    template_name = 'b24online/Questionnaires/questionForm.html'
    success_url = reverse_lazy('questionnaires:main')

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not can_manage_product(request.user,
                                  self.object.questionnaire.item):
            return HttpResponseRedirect(reverse('denied'))
        return super(QuestionUpdate, self) \
            .dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(
            request,
            instance=self.object,
        )
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        form = self.form_class(
            request,
            instance=self.object,
            data=request.POST,
            files=request.FILES
        )
        if form.is_valid():
            form.save()
            success_url = reverse(
                'questionnaires:detail',
                kwargs={
                    'item_id': self.object.questionnaire.id,
                })
            return HttpResponseRedirect(success_url)
        return self.render_to_response(self.get_context_data(form=form))


class RecommendationCreate(LoginRequiredMixin, ItemCreate):
    """
    The view for creating.
    """
    model = Recommendation
    form_class = RecommendationForm
    template_name = 'b24online/Questionnaires/recommendationForm.html'
    success_url = reverse_lazy('questionnaires:main')

    def dispatch(self, request, *args, **kwargs):
        self.object = None
        self.item_id = kwargs.pop('item_id')
        try:
            _questionnaire = Questionnaire.objects.get(pk=self.item_id)
        except:
            return HttpResponseRedirect(reverse('denied'))
        else:
            if not can_manage_product(request.user, _quetionnaire):
                return HttpResponseRedirect(reverse('denied'))

        return super(RecommendationCreate, self) \
            .dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(
            request,
            item_id=self.item_id
        )
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        form = self.form_class(
            request,
            item_id=self.item_id,
            data=request.POST,
            files=request.FILES
        )
        if form.is_valid():
            form.save()
            success_url = reverse(
                'questionnaires:detail',
                kwargs={
                    'item_id': self.item_id,
                })
            return HttpResponseRedirect(success_url)
        return self.render_to_response(self.get_context_data(form=form))


class RecommendationUpdate(LoginRequiredMixin, ItemUpdate):
    """
    The view for creating.
    """
    model = Recommendation
    form_class = RecommendationForm
    template_name = 'b24online/Questionnaires/recommendationForm.html'
    success_url = reverse_lazy('questionnaires:main')

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not can_manage_product(request.user,
                                  self.object.questionnaire.item):
            return HttpResponseRedirect(reverse('denied'))
        return super(RecommendationUpdate, self) \
            .dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(
            request,
            instance=self.object,
        )
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        form = self.form_class(
            request,
            instance=self.object,
            data=request.POST,
            files=request.FILES
        )
        if form.is_valid():
            form.save()
            success_url = reverse(
                'questionnaires:detail',
                kwargs={
                    'item_id': self.object.questionnaire.id,
                })
            return HttpResponseRedirect(success_url)
        return self.render_to_response(self.get_context_data(form=form))


@login_required
def questionnaire_case_answers(request, pk, participant_type, **kwargs):
    model = QuestionnaireCase
    template_name = 'b24online/Questionnaires/questionnaireCaseAnswers.html'
    if request.is_ajax():
        try:
            instance = QuestionnaireCase.objects.get(pk=pk)
        except QuestionnaireCase.DoesNotExist:
            raise Http404(_('There is no such QuestionnaireCase with ID={0}') \
                          .format(pk))
        else:
            if not can_manage_product(request.user,
                                      instance.questionnaire.item):
                return HttpResponseRedirect(reverse('denied'))

            answers = instance.get_answers(participant_type)
            data = {
                'code': 'success',
                'msg': render_to_string(
                    template_name,
                    {'instance': instance,
                     'answers': answers,
                     'responsive': instance.get_participant(participant_type)},
                    request,
                )
            }
            return JsonResponse(data)

    return HttpResponseBadRequest()


@login_required
def questionnaire_case_coincedences(request, pk, **kwargs):
    model = QuestionnaireCase
    template_name = 'b24online/Questionnaires/questionnaireCaseCoincedences.html'
    if request.is_ajax():
        try:
            instance = QuestionnaireCase.objects.get(pk=pk)
        except QuestionnaireCase.DoesNotExist:
            raise Http404(_('There is no such QuestionnaireCase with ID={0}') \
                          .format(pk))
        else:
            if not can_manage_product(request.user,
                                      instance.questionnaire.item):
                return HttpResponseRedirect(reverse('denied'))

            coincedences = instance.get_coincedences()
            data = {
                'code': 'success',
                'msg': render_to_string(
                    template_name,
                    {'instance': instance,
                     'coincedences': coincedences,
                     },
                    request,
                )
            }
            return JsonResponse(data)

    return HttpResponseBadRequest()
