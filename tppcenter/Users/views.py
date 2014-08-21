import json

from haystack.backends import SQ
from haystack.query import SearchQuerySet
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _

from appl.func import filterLive, setPaginationForSearchWithValues, getPaginatorRange
from appl.models import Country, Cabinet
from core.models import Item
from tppcenter.cbv import ItemsList


class get_users_list(ItemsList):

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
