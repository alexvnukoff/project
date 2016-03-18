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
from usersites.Questionnaires.forms import InviteForm

logger = logging.getLogger(__name__)
        

class QuestionnaireDetail(UserTemplateMixin, ItemDetail):
    model = Questionnaire
    template_name = '{template_path}/Questionnaires/detail.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = InviteForm(self.request, self.object)
        return self.render_to_response(
            self.get_context_data(form=form, *args, **kwargs)
        )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = InviteForm(
            self.request,
            self.object,
            data=self.request.POST
        )
        if form.is_valid():
            form.save()
            
        return self.render_to_response(
            self.get_context_data(form=form, *args, **kwargs)
        )

