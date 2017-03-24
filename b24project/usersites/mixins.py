# -*- encoding: utf-8 -*-
from usersites.redisHash import get_usersite_objects

DEFAULT_TEMPLATE_PATH = 'usersites'


class UserTemplateMixin:
    def __init__(self, **kwargs):
        self.usersite, self.template, self.organization = get_usersite_objects()

    def get_template_names(self):
        if self.template is not None:
            self.template_name = self.template_name.format(template_path=self.template.folder_name)
        else:
            self.template_name = self.template_name.format(template_path=DEFAULT_TEMPLATE_PATH)
        return super(UserTemplateMixin, self).get_template_names()
