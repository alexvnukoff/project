from django.core.exceptions import ObjectDoesNotExist

from tpp.DynamicSiteMiddleware import get_current_site

DEFAULT_TEMPLATE_PATH = 'usersites'


class UserTemplateMixin:
    def get_template_names(self):
        site = get_current_site()
        try:
            user_site = site.user_site
            user_site.refresh_from_db()
            if user_site.user_template is not None:
                folder_template = user_site.user_template.folder_name
                self.template_name = self.template_name.format(template_path=folder_template)
            else:
                self.template_name = self.template_name.format(template_path=DEFAULT_TEMPLATE_PATH)
        except ObjectDoesNotExist:
            self.template_name = self.template_name.format(template_path=DEFAULT_TEMPLATE_PATH)
        return super(UserTemplateMixin, self).get_template_names()
