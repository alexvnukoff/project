from django.utils.translation import ugettext as _

from b24online.models import Video
from usersites.cbv import ItemList, ItemDetail
from usersites.mixins import UserTemplateMixin


class VideoDetail(UserTemplateMixin, ItemDetail):
    model = Video
    template_name = '{template_path}/Video/detailContent.html'
