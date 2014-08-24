from django.conf import settings
from django.utils.translation import ugettext as _
from haystack.backends import SQ
from haystack.query import SearchQuerySet
from appl.models import Greeting
from tppcenter.cbv import ItemDetail, ItemsList


class get_greetings_list(ItemsList):

    #pagination url
    url_paginator = "greetings:paginator"

    #Lists of required scripts and styles for ajax request
    styles = [
        settings.STATIC_URL + 'tppcenter/css/news.css',
        settings.STATIC_URL + 'tppcenter/css/company.css'
    ]

    current_section = _("Greetings")

    #allowed filter list
    filterList = ['tpp', 'country', 'company', 'branch']

    model = Greeting

    template_name = 'Greetings/index.html'

    def get_queryset(self):

        sqs = SearchQuerySet().models(self.model)

        q = self.request.GET.get('q', '')

        if q != '': #Search for content
            sqs = sqs.filter(SQ(title=q) | SQ(text=q))

        return sqs


class get_greeting_detail(ItemDetail):

    model = Greeting
    template_name = 'Greetings/detailContent.html'

    current_section = _("Greetings")

    def get_queryset(self):
        return SearchQuerySet().models(self.model)