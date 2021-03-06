from django.utils.translation import ugettext as _

from b24online.cbv import ItemsList
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
        self.template_name = 'b24online/Users/contentPage.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'b24online/Users/index.html'

    def get_queryset(self):
        return Profile.get_active_objects().all()
