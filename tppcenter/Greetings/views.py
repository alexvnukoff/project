from django.conf import settings
from django.utils.translation import ugettext as _

from b24online.cbv import ItemsList, ItemDetail
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


class GreetingDetail(ItemDetail):
    model = Greeting
    template_name = 'Greetings/detailContent.html'

    current_section = _("Greetings")