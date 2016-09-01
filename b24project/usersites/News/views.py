from django.utils.translation import ugettext as _

from b24online.models import News
from usersites.cbv import ItemList, ItemDetail
from usersites.mixins import UserTemplateMixin

class NewsList(UserTemplateMixin, ItemList):
    model = News
    template_name = '{template_path}/News/contentPage.html'
    paginate_by = 10
    url_paginator = "news:paginator"
    current_section = _("News")
    title = _("News")


class NewsDetail(UserTemplateMixin, ItemDetail):
    model = News
    template_name = '{template_path}/News/detailContent.html'
