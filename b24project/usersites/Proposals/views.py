from django.utils.translation import ugettext as _
from b24online.models import BusinessProposal

from usersites.cbv import ItemList, ItemDetail

from usersites.mixins import UserTemplateMixin

class BusinessProposalList(UserTemplateMixin, ItemList):
    model = BusinessProposal
    template_name = '{template_path}/Proposals/contentPage.html'
    paginate_by = 10
    url_paginator = "proposal:paginator"
    current_section = _("Business proposals")
    title = _("Business proposals")


class BusinessProposalDetail(UserTemplateMixin, ItemDetail):
    model = BusinessProposal
    template_name = '{template_path}/Proposals/detailContent.html'
