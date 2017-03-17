# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import ugettext as _
from appl import func
from django.views.generic import TemplateView
from usersites.cbv import ItemList
from usersites.mixins import UserTemplateMixin
from b24online.models import Branch, Company
from centerpokupok.models import B2CProductCategory, B2CProduct


class BIndexView(UserTemplateMixin, TemplateView):
    template_name = '{template_path}/BusinessIndex/contentPage.html'
    current_section = ""

    def get_branches(self):
        children = self.organization.children.all()
        return Branch.objects.filter(company__in=children).distinct()

    def get_context_data(self, **kwargs):
        context = super(BIndexView, self).get_context_data(**kwargs)

        context = {
            'current_section': self.current_section,
            'organization': self.organization,
            'branches': self.get_branches(),
            'title': _("Business Index")
        }

        return context



class BIBranchView(UserTemplateMixin, ItemList):
    template_name = '{template_path}/BusinessIndex/branchPage.html'
    title = _("Business Index")
    url_paginator = "business_index:paginator"

    paginate_by = 15

    def dispatch(self, request, *args, **kwargs):
        self.branch_id = kwargs['pk']
        return super(BIBranchView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Company.get_active_objects().filter(
            branches=self.branch_id, parent=self.organization)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data()
        context_data.update(
            url_paginator=self.get_url_paginator(),
            paginator_range=func.get_paginator_range(context_data['page_obj']),
            title=self.get_title(),
            url_parameter=self.branch_id,
            current_section=self.get_current_section()
        )

        return context_data
