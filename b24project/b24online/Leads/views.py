# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import transaction
from django.http import HttpResponseRedirect, Http404
from django.utils.translation import ugettext as _
from guardian.mixins import LoginRequiredMixin
from b24online.models import Branch, Organization, LeadsStore
from b24online.cbv import ItemsList, ItemUpdate
from django.views.generic import UpdateView, DeleteView
from b24online.Leads.forms import LeadEditForm


class IndexLeadsList(LoginRequiredMixin, ItemsList):
    # pagination url
    paginate_by = "30"
    url_my_paginator = "leads:main_paginator"

    current_section = _("Leads")
    model = LeadsStore

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'b24online/Leads/index.html'

    def optimize_queryset(self, queryset):
        return queryset.prefetch_related(
                'organization',
                'organization__countries'
                )

    def get_queryset(self):
        queryset = super(IndexLeadsList, self).get_queryset()

        if self.is_my():
            if self.request.user.is_admin:
                queryset = self.model.get_active_objects().filter(
                    is_active=True
                    ).order_by('-id')
            else:
                current_org = self._current_organization
                queryset = self.model.get_active_objects().filter(
                    organization=current_org,
                    is_active=True
                    ).order_by('-id')

        return queryset

    def get_context_data(self, **kwargs):
        context = super(IndexLeadsList, self).get_context_data(**kwargs)
        context['total_objects'] = self.get_queryset().count
        return context


class GoLeadDelete(DeleteView):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj.has_perm(request.user):
            return HttpResponseRedirect(reverse('denied'))
        return super().dispatch(request, *args, **kwargs)

    success_url = reverse_lazy('leads:main')
    model = LeadsStore

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)


class GoLeadUpdate(ItemUpdate):
    model = LeadsStore
    form_class = LeadEditForm
    template_name = 'b24online/Leads/addForm.html'
    success_url = reverse_lazy('leads:main')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj.has_perm(request.user):
            return HttpResponseRedirect(reverse('denied'))
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form(self.get_form_class())
        return self.render_to_response(self.get_context_data(form=form))

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self):
        return self.render_to_response(self.get_context_data(form=form))

