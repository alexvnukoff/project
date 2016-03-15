# -*- encoding: utf-8 -*-

import logging

from django.http import HttpResponse, Http404
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import (DetailView, ListView, View,
                                  TemplateView)

from b24online.models import Questionnaire, Question, Answer
from guardian.mixins import LoginRequiredMixin
from b24online.cbv import (ItemsList, ItemDetail, ItemUpdate, ItemCreate, 
                           ItemDeactivate)
from b24online.Questionnaires.forms import QuestionnaireForm
from b24online.utils import get_by_content_type

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
        logger.debug('OKOKOKOKo')
        self.content_type_id = self.kwargs.get('content_type_id')
        self.product_id = self.kwargs.get('item_id')
        self.product = None
        if self.content_type_id and self.product_id:
            self.product = get_by_content_type(
                self.content_type_id, 
                self.product_id
            )
            if not self.product:
                raise Http404(_('There is no such instance'))
        
        return super(QuestionnaireList, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super(QuestionnaireList, self).get_queryset()
        logger.debug(qs)
        if self.product:
            qs = qs.filter(
                content_type_id=self.content_type_id,
                object_id=self.product_id
            )    
        return qs

    def get_context_data(self, **kwargs):
        logger.debug('Step 1')
        context = super(QuestionnaireList, self).get_context_data(**kwargs)
        logger.debug(context)
        context.update({
            'product': self.product,
        })
        return context
        

class QuestionnaireUpdate(TemplateView):
    template_name = 'b24online/Questionnaires/form.html'


