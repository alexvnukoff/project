from django.utils.translation import ugettext as _

from b24online.models import Exhibition
from usersites.cbv import ItemList, ItemDetail
from usersites.mixins import UserTemplateMixin


class ExhibitionDetail(UserTemplateMixin, ItemDetail):
    model = Exhibition
    template_name = '{template_path}/Exhibitions/detailContent.html'
