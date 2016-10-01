# -*- encoding: utf-8 -*-

import json
import logging

from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.http import JsonResponse
from django.utils.translation import ugettext as _
from django.conf import settings

from b24online.cbv import ItemsList, ItemDetail, ItemUpdate, ItemCreate, ItemDeactivate
from jobs.models import Requirement, Resume
from b24online.models import StaffGroup
from b24online.Vacancy.forms import RequirementForm


class RequirementList(ItemsList):
    # pagination url
    url_paginator = "vacancy:paginator"
    url_my_paginator = "vacancy:my_main_paginator"

    # Lists of required scripts and styles for ajax request
    styles = [
        settings.STATIC_URL + 'b24online/css/news.css',
        settings.STATIC_URL + 'b24online/css/company.css'
    ]

    current_section = _("Job requirements")
    addUrl = 'vacancy:add'

    # allowed filter list
    # filter_list = ['tpp', 'country', 'company', 'branch']

    model = Requirement

    def ajax(self, request, *args, **kwargs):
        self.template_name = 'b24online/Vacancy/contentPage.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'b24online/Vacancy/index.html'

    def optimize_queryset(self, queryset):
        return queryset.select_related('country')

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.is_my():
            current_org = self._current_organization

            if current_org is not None:
                queryset = self.model.get_active_objects().filter(vacancy__department__organization_id=current_org)
            else:
                queryset = queryset.none()

        return queryset


class RequirementDetail(ItemDetail):
    model = Requirement
    template_name = 'b24online/Vacancy/detailContent.html'

    current_section = _("Vacancy")
    addUrl = 'vacancy:add'

    def _get_user_resume_list(self):
        return Resume.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(RequirementDetail, self).get_context_data(**kwargs)

        if self.request.user.is_authenticated():
            context['resumes'] = self._get_user_resume_list()

        return context


class RequirementDelete(ItemDeactivate):
    model = Requirement


def send_resume(request):
    response = ""
    if request.is_ajax():
        if request.user.is_authenticated() and request.POST.get('VACANCY', False):
            if request.POST.get('RESUME', False):
                requirement = request.POST.get('VACANCY', "")
                resume = request.POST.get('RESUME', '')
                # if Relationship.objects.filter(parent=Requirement.objects.get(pk=int(requirement)),
                #                                child=Resume.objects.get(pk=int(resume))).exists():
                #     response = _('You cannot send more than one resume at the same job position.')
                # else:
                # Resume.setRelRelationship(parent=Requirement.objects.get(pk=int(requirement)),
                #                                 child=Resume.objects.get(pk=int(resume)), user=request.user)
                # response = _('You have successfully sent the resume.')

            else:
                response = _('Resume  are required')
        else:
            response = _('Only registred users can send resume')

        return HttpResponse(response)


class RequirementCreate(ItemCreate):
    org_required = False
    model = Requirement
    form_class = RequirementForm
    template_name = 'b24online/Vacancy/addForm.html'
    success_url = reverse_lazy('vacancy:main')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request

        return kwargs

    def form_invalid(self, form):
        return super().form_invalid(form)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        form.instance.vacancy = form.cleaned_data.get('vacancy')

        result = super().form_valid(form)
        self.object.reindex()

        return result


class RequirementUpdate(ItemUpdate):
    model = Requirement
    form_class = RequirementForm
    template_name = 'b24online/Vacancy/addForm.html'
    success_url = reverse_lazy('vacancy:main')

    def form_invalid(self, form):
        return super().form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request

        return kwargs

    def form_valid(self, form):
        form.instance.updated_by = self.request.user

        result = super().form_valid(form)

        if form.changed_data:
            if 'vacancy' in form.changed_data:
                form.instance.vacancy = form.cleaned_data.get('vacancy')

            self.object.reindex()

        return result


def get_staffgroup_options(request, *args, **kwargs):
    """
    Return the :class:`StaffGroup` options for select field.
    """
    options = [{'name': '------', 'id': ''}]
    for item in StaffGroup.objects.order_by('group__name'):
        options.append({'name': item.group.name, 'id': item.pk})
    return JsonResponse(options)
