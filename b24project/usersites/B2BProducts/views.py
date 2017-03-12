# -*- encoding: utf-8 -*-
import json
import logging
from collections import OrderedDict
from django.utils.translation import ugettext as _
from django.http import HttpResponse
from b24online.models import B2BProduct, B2BProductCategory
from b24online.search_indexes import B2BProductIndex
from tpp.DynamicSiteMiddleware import get_current_site
from usersites.cbv import ItemDetail, ItemList
from usersites.mixins import UserTemplateMixin
from django.views.generic import TemplateView


logger = logging.getLogger(__name__)


class B2BProductListDetail(UserTemplateMixin, ItemDetail):
    model = B2BProduct
    filter_key = 'company'
    template_name = '{template_path}/B2BProducts/detailContent.html'


class B2BCategoriesView(UserTemplateMixin, TemplateView):
    template_name = '{template_path}/B2BProducts/categoriesPage.html'
    current_section = ""

    def get_context_data(self, **kwargs):
        context = super(B2BCategoriesView, self).get_context_data(**kwargs)

        context = {
            'current_section': self.current_section,
            'organization': self.organization,
            'title': _("Categories"),
        }

        return context
