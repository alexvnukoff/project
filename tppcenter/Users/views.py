from django.utils.translation import ugettext as _

from tppcenter.cbv import ItemsList
from b24online.models import Profile


class UserList(ItemsList):
    paginate_by = 12

    #pagination url
    url_paginator = "users:paginator"

    current_section = _("Users")

    #allowed filter list
    # filter_list = ['country']

    model = Profile

    def ajax(self, request, *args, **kwargs):
        self.template_name = 'Users/contentPage.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'Users/index.html'

    def get_queryset(self):
        return Profile.active_objects.all()
