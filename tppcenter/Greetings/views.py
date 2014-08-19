from django.conf import settings
from django.utils.translation import ugettext as _
from appl.models import Greeting
from tppcenter.cbv import ItemDetail, ItemsList


class get_greetings_list(ItemsList):

    #pagination url
    url_paginator = "greetings:paginator"
    url_my_paginator = "greetings:my_main_paginator"

    #Lists of required scripts and styles for ajax request
    styles = [
        settings.STATIC_URL + 'tppcenter/css/news.css',
        settings.STATIC_URL + 'tppcenter/css/company.css'
    ]

    current_section = _("Greetings")
    addUrl = 'greetings:add'

    #allowed filter list
    filterList = ['tpp', 'country', 'company', 'branch']

    model = Greeting

    template_name = 'Greetings/index.html'


class get_greeting_detail(ItemDetail):

    model = Greeting
    template_name = 'Greetings/detailContent.html'

    current_section = _("Greetings")
    addUrl = 'greetings:add'