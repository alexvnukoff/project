from django.conf import settings
from django.utils.translation import ugettext as _

from b24online.cbv import ItemsList, ItemDetail
from b24online.models import Greeting


class GreetingList(ItemsList):
    #pagination url
    url_paginator = "greetings:paginator"

    # Sorting fields
    sortField1 = 'name'
    sortField2 = None
    order1 = 'desc'
    order2 = None

     # Fields to sort by
    sortFields = {
        'name': 'name'
    }
 
    #Lists of required scripts and styles for ajax request
    styles = [
        settings.STATIC_URL + 'b24online/css/news.css',
        settings.STATIC_URL + 'b24online/css/company.css'
    ]

    current_section = _("Greetings")

    #allowed filter list
    filterList = []

    model = Greeting
    template_name = 'b24online/Greetings/index.html'

    def get_queryset(self):
        queryset = self.model.objects.all()
        return self.optimize_queryset(queryset)


class GreetingDetail(ItemDetail):
    model = Greeting
    template_name = 'b24online/Greetings/detailContent.html'

    current_section = _("Greetings")

    def get_queryset(self):
        return self.model.objects.all()
