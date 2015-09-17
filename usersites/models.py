import os

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db import models
from b24online.custom import CustomImageField

from b24online.models import Organization, image_storage, Gallery
from b24online.utils import generate_upload_path
from core import tasks

templates_root = "%s/../templates" % settings.MEDIA_ROOT


class ExternalSiteTemplate(models.Model):
    name = models.CharField(max_length=100)
    folder_name = models.FilePathField(allow_folders=True, path=templates_root)

    def theme_folder(self):
        return os.path.basename(self.folder_name)

    def __str__(self):
        return self.name


class UserSite(models.Model):
    template = models.ForeignKey(ExternalSiteTemplate, blank=True, null=True)
    organization = models.ForeignKey(Organization)
    slogan = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)
    logo = CustomImageField(upload_to=generate_upload_path, storage=image_storage, sizes=['big'], max_length=255)
    footer_text = models.TextField(null=True, blank=True)
    site = models.OneToOneField(Site, null=True, blank=True, related_name='user_site')
    domain_part = models.CharField(max_length=100, null=False, blank=False)
    galleries = GenericRelation(Gallery, related_query_name='sites')

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def upload_images(self, is_new_logo, changed_galleries=None):
        params = []

        if is_new_logo:
            params.append({
                'file': self.logo.path,
                'sizes': {
                    'big': {'box': (220, 120), 'fit': True}
                }
            })

        if changed_galleries is not None:
            for image_path in changed_galleries:
                params.append({
                    'file': image_path,
                    'sizes': {
                        'big': {'box': (400, 105), 'fit': True},
                    }
                })

        tasks.upload_images.delay(*params)

    @property
    def root_domain(self):
        if self.site.domain == self.domain_part:
            return None

        # if settings.USER_SITES_DOMAIN is changed, then we have 2+ sites with different root domains
        # eg. subdomain.tppcenter.com, subdomain.b24online.com
        # so we have the subdomain part and we need to get the root domain

        return self.site.domain.replace("%s." % self.domain_part, '')

    def get_gallery(self, user):
        model_type = ContentType.objects.get_for_model(self)
        gallery, _ = Gallery.objects.get_or_create(content_type=model_type, object_id=self.pk, defaults={
            'created_by': user,
            'updated_by': user
        })

        return gallery
