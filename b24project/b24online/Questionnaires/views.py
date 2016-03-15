# -*- encoding: utf-8 -*-

import logging

from django.http import HttpResponse
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse, reverse_lazy

from b24online.models import Questionnaire, Question, Answer
from guardian.mixins import LoginRequiredMixin
from b24online.cbv import (ItemsList, ItemDetail, ItemUpdate, ItemCreate, 
                           ItemDeactivate)
from b24online.Questionnaires.forms import QuestionnaireForm

logger = logging.getLogger(__name__)


class QuestionnaireCreate(LoginRequiredMixin, ItemCreate):
    model = Questionnaire
    form_class = QuestionnaireForm
    template_name = 'b24online/Questionnaires/form.html'
    success_url = reverse_lazy('questionnaires:main')

    def get(self, request, *args, **kwargs):
        self.object = None
        content_type_id = kwargs.pop('content_type_id')
        item_id = kwargs.pop('item_id')
        form = self.form_class(
            request, 
            content_type_id=content_type_id,
            item_id=item_id,
        )
        return self.render_to_response(
            self.get_context_data(form=form)
        )

    def post(self, request, *args, **kwargs):
        self.object = None
        content_type_id = kwargs.pop('content_type_id')
        item_id = kwargs.pop('item_id')
        form = self.form_class(
            request, 
            content_type_id=content_type_id,
            item_id=item_id,
            data=request.POST,
            files=request.FILES
        )
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(self.success_url)
        return self.render_to_response(self.get_context_data(form=form))


class QuestionnaireList(LoginRequiredMixin, ItemsList):
    model = Questionnaire
    template_name = 'b24online/Questionnaires/list.html'


class QuestionnaireUpdate(TemplateView):
    template_name = 'b24online/Questionnaires/form.html'

