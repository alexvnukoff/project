# -*- encoding: utf-8 -*-

"""
The views for Questionnaires, Questions etc
"""

import logging

from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse, reverse_lazy
from b24online.models import Questionnaire
from guardian.mixins import LoginRequiredMixin
from b24online.cbv import ItemDetail
from usersites.mixins import UserTemplateMixin


logger = logging.getLogger(__name__)
        

class QuestionnaireDetail(UserTemplateMixin, ItemDetail):
    model = Questionnaire
    template_name = '{template_path}/Questionnaires/detail.html'

    def get_context_data(self, **kwargs):
        context = super(QuestionnaireDetail, self).get_context_data(**kwargs)
        questionnaire = context.get('item')
        self._product = questionnaire.item
        context.update({
            'product': self._product,
        })
        return context
