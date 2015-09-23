from django.utils.translation import ugettext as _

from b24online.models import News
from usersites.cbv import ItemList, ItemDetail


class NewsList(ItemList):
    model = News
    template_name = 'News/contentPage.html'
    paginate_by = 10
    url_paginator = "news:paginator"
    current_section = _("News")
    title = _("News")


class NewsDetail(ItemDetail):
    model = News
    template_name = 'News/detailContent.html'
