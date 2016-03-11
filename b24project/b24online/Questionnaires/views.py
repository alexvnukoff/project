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

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return self.render_to_response(
            self.get_context_data(form=form)
        )

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return self.form_valid(form) if form.is_valid() \
            else self.form_invalid(form)

    def form_valid(self, form, additional_page_form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        self.object = form.save()
        self.object.upload_image()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, additional_page_form):
        context_data = self.get_context_data(form=form)
        return self.render_to_response(context_data)


class QuestionnaireList(TemplateView):
    template_name = 'b24online/Questionnaires/index.html'
