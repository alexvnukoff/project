# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView
from usersites.mixins import UserTemplateMixin
from centerpokupok.models import B2CProductCategory, B2CProduct


class BIndexView(UserTemplateMixin, TemplateView):
    template_name = '{template_path}/BusinessIndex/contentPage.html'
    current_section = ""

    def get_context_data(self, **kwargs):
        context = super(BIndexView, self).get_context_data(**kwargs)

        context = {
            'current_section': self.current_section,
            'organization': self.organization,
            'title': _("Business Index"),
        }

        return context

