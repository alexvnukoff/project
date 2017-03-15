# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView, ListView
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



class BIBranchView(UserTemplateMixin, ListView):
    template_name = '{template_path}/BusinessIndex/branchPage.html'
    current_section = ""

    def dispatch(self, request, *args, **kwargs):
        self.branch_id = kwargs['pk']
        return super(BIBranchView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Company.get_active_objects().filter(
            branches=self.branch_id, parent=self.organization)

    # def get_context_data(self, **kwargs):
    #     context = super(BIBranchView, self).get_context_data(**kwargs)

    #     companies = Company.get_active_objects()
    #     context = {
    #         'current_section': self.current_section,
    #         'organization': self.organization,
    #         'branches': self.get_branches(),
    #         'title': _("Business Index")
    #     }

    #     return context