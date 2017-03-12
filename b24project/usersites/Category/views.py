# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView
from usersites.mixins import UserTemplateMixin
from centerpokupok.models import B2CProductCategory, B2CProduct



class CategoriesView(UserTemplateMixin, TemplateView):
    template_name = '{template_path}/Category/CategoriesView.html'
    current_section = ""

    def get_context_data(self, **kwargs):
        context = super(CategoriesView, self).get_context_data(**kwargs)

        context = {
            'current_section': self.current_section,
            'organization': self.organization,
            'title': _("Categories"),
        }

        return context

