# -*- encoding: utf-8 -*-

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


class QuestionnaireCreate(ItemCreate):
    model = Questionnaire
    form_class = QuestionnaireForm
    template_name = 'b24online/Questionnaires/addForm.html'
    success_url = reverse_lazy('questionnaires:main')

    def dispatch(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        return super(QuestionnaireCreate, self)\
            .dispatch(request, *args, **kwargs)
        
    def get(self, request, *args, **kwargs):
        form = self.form_class(request)
        return self.render_to_response(
            self.get_context_data(form=form)
        )

    def post(self, request, *args, **kwargs):
        form = self.form_class(request, instance=self.object, 
                               data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(self.get_success_url())
        return self.render_to_response(self.get_context_data(form=form))


class QuestionnaireList(TemplateView):
    template_name = 'b24online/Questionnaires/index.html'
