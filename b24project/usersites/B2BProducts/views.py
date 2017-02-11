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

logger = logging.getLogger(__name__)


class B2BProductListDetail(UserTemplateMixin, ItemDetail):
    model = B2BProduct
    filter_key = 'company'
    template_name = '{template_path}/B2BProducts/detailContent.html'


class B2BProductJsonData(ProductJsonData):
    model_class = B2BProduct
    search_index_class = B2BProductIndex
