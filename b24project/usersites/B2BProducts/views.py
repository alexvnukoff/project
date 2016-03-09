from b24online.models import B2BProduct
from usersites.cbv import ItemDetail
from usersites.mixins import UserTemplateMixin

class B2BProductListDetail(UserTemplateMixin, ItemDetail):
    model = B2BProduct
    filter_key = 'company'
    template_name = '{template_path}/B2BProducts/detailContent.html'

