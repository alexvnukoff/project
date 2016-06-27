from django.utils.translation import ugettext as _

from b24online.models import News
from usersites.cbv import ItemList, ItemDetail
from usersites.mixins import UserTemplateMixin


class NewsDetail(UserTemplateMixin, ItemDetail):
    model = News
    template_name = '{template_path}/News/detailContent.html'
