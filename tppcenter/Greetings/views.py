from django.conf import settings
from django.utils.translation import ugettext as _

from tppcenter.cbv import ItemsList, ItemDetail
from b24online.models import Greeting


class GreetingList(ItemsList):
    #pagination url
    url_paginator = "greetings:paginator"

     # Fields to sort by
    sortFields = {
        'name': 'name'
    }
 
    #Lists of required scripts and styles for ajax request
    styles = [
        settings.STATIC_URL + 'tppcenter/css/news.css',
        settings.STATIC_URL + 'tppcenter/css/company.css'
    ]

    current_section = _("Greetings")

    #allowed filter list
    filterList = []

    model = Greeting
    template_name = 'Greetings/index.html'

    def get_queryset(self):
        if self.is_filtered() and not self.is_my():
            return self.get_filtered_items().sort(*self._get_sorting_params())

        queryset = self.model.objects.order_by(*self._get_sorting_params())
        return self.optimize_queryset(queryset)


class GreetingDetail(ItemDetail):
    model = Greeting
    template_name = 'Greetings/detailContent.html'

    current_section = _("Greetings")

    def get_queryset(self):
        return self.model.objects.all()
