from haystack.query import SearchQuerySet
from django.utils.translation import ugettext as _

from appl.models import Cabinet
from tppcenter.cbv import ItemsList


class get_users_list(ItemsList):

    paginate_by = 12

    #pagination url
    url_paginator = "users:paginator"

    current_section = _("Users")

    #allowed filter list
    filterList = ['country']

    model = Cabinet

    def ajax(self, request, *args, **kwargs):
        self.template_name = 'Users/contentPage.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'Users/index.html'

    def get_queryset(self):

        sqs = SearchQuerySet().models(self.model)

        searchFilter = self.filterLive()

        if searchFilter:
            sqs = sqs.filter(searchFilter)

        q = self.request.GET.get('q', '')

        if q != '': #Search for content
            sqs = sqs.filter(text=q)

        return sqs.order_by('text')