# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.db import transaction
from django.http import HttpResponseRedirect, Http404
from django.utils.translation import ugettext as _
from guardian.mixins import LoginRequiredMixin
from b24online.models import Branch, Organization, LeadsStore
from b24online.cbv import (ItemsList, ItemDetail, ItemUpdate, ItemCreate,
                        ItemDeactivate, DeleteGalleryImage, GalleryImageList,
                        DocumentList, DeleteDocument)


class IndexLeadsList(LoginRequiredMixin, ItemsList):
    # pagination url
    url_my_paginator = "leads:main_paginator"

    current_section = _("Leads")
    model = LeadsStore

    def ajax(self, request, *args, **kwargs):
        self.template_name = 'b24online/Leads/contentPage.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'b24online/Leads/index.html'

    def optimize_queryset(self, queryset):
        return queryset.prefetch_related('organization', 'organization__countries')

    def get_queryset(self):
        queryset = super(IndexLeadsList, self).get_queryset()

        if self.is_my():
            current_org = self._current_organization
            queryset = self.model.get_active_objects().filter(organization=current_org)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(IndexLeadsList, self).get_context_data(**kwargs)
        context['total_objects'] = self.get_queryset().count
        return context
