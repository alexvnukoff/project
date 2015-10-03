from django.utils.translation import ugettext as _
from b24online.models import BusinessProposal

from usersites.cbv import ItemList, ItemDetail


class BusinessProposalList(ItemList):
    model = BusinessProposal
    template_name = 'usersites/Proposals/contentPage.html'
    paginate_by = 10
    url_paginator = "proposal:paginator"
    current_section = _("Business proposals")
    title = _("Business proposals")


class BusinessProposalDetail(ItemDetail):
    model = BusinessProposal
    template_name = 'usersites/Proposals/detailContent.html'
