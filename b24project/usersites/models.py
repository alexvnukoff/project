# -*- coding: utf-8 -*-

import os
import logging

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db import models
from django.utils import timezone
from b24online.custom import CustomImageField
from b24online.models import Organization, image_storage, Gallery, ActiveModelMixing, GalleryImage
from b24online.utils import generate_upload_path
from django.utils.translation import ugettext as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from django.contrib.postgres.fields import JSONField

logger = logging.getLogger(__name__)


class ExternalSiteTemplate(models.Model):
    name = models.CharField(max_length=255)
    folder_name = models.CharField(max_length=255)

    def theme_folder(self):
        return os.path.basename(self.folder_name)

    def __str__(self):
        return self.name


class UserSiteTemplate(models.Model):
    name = models.CharField(max_length=255)
    thumbnail = CustomImageField(upload_to=generate_upload_path, storage=image_storage, sizes=['big', 'small'],
                                 max_length=255)
    folder_name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


@receiver(post_save, sender=UserSiteTemplate)
def uploadTemplateImage(sender, instance, **kwargs):
    from core import tasks
    params = []
    params.append({
        'file': instance.thumbnail.path,
        'sizes': {
            'small': {'box': (200, 200), 'fit': True},
        }
    })

    tasks.upload_images.delay(*params)


class UserSite(ActiveModelMixing, models.Model):

    LANG_LIST = [('auto', 'Auto')] + list(settings.LANGUAGES)

    template = models.ForeignKey(ExternalSiteTemplate, blank=True, null=True)
    user_template = models.ForeignKey(UserSiteTemplate, blank=True, null=True)
    organization = models.ForeignKey(Organization, related_name='user_site')
    slogan = models.CharField(max_length=2048, blank=True, null=True)
    language = models.CharField(max_length=4, choices=LANG_LIST, default='auto')
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    logo = CustomImageField(upload_to=generate_upload_path, storage=image_storage, sizes=['big'], max_length=255)
    footer_text = models.TextField(null=True, blank=True)
    site = models.OneToOneField(Site, null=True, blank=True, related_name='user_site')
    domain_part = models.CharField(max_length=100, null=False, blank=False)
    galleries = GenericRelation(Gallery, related_query_name='sites')
    metadata = JSONField(default=dict())

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def upload_images(self, is_new_logo, changed_galleries=None, changed_banners=None):
        from core import tasks
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

        if changed_banners is not None:
            for image_path in changed_banners:
                params.append({
                    'file': image_path,
                    'sizes': {
                        'big': {'box': (150, 150), 'fit': False},
                    }
                })

        tasks.upload_images.delay(*params)

    @property
    def root_domain(self):
        if self.site.domain == self.domain_part:
            return None

        # if settings.USER_SITES_DOMAIN is changed, then we have 2+ sites with different root domains
        # eg. subdomain.b24online.com, subdomain.b24online.com
        # so we have the subdomain part and we need to get the root domain

        return self.site.domain.replace("%s." % self.domain_part, '')

    def get_gallery(self, user):
        model_type = ContentType.objects.get_for_model(self)
        gallery, _ = Gallery.objects.get_or_create(content_type=model_type, object_id=self.pk, defaults={
            'created_by': user,
            'updated_by': user
        })

        return gallery

    @property
    def slider_images(self):
        model_type = ContentType.objects.get_for_model(self)
        return GalleryImage.objects.filter(gallery__content_type=model_type, gallery__object_id=self.pk)

    @property
    def facebook(self):
        if self.metadata:
            return self.metadata.get('facebook', '')
        return None

    @property
    def youtube(self):
        if self.metadata:
            return self.metadata.get('youtube', '')
        return None

    @property
    def twitter(self):
        if self.metadata:
            return self.metadata.get('twitter', '')
        return None

    @property
    def instagram(self):
        if self.metadata:
            return self.metadata.get('instagram', '')
        return None

    @property
    def vkontakte(self):
        if self.metadata:
            return self.metadata.get('vkontakte', '')
        return None

    @property
    def odnoklassniki(self):
        if self.metadata:
            return self.metadata.get('odnoklassniki', '')
        return None

    def __str__(self):
        return self.domain_part

    def clear_cache(self):
        if self.site.pk:
            # Call save signal to clear the cache
            self.site.save()
        site_cache = 'usersite_lang_{0}'.format(self.site.pk)
        if cache.get(site_cache):
            cache.delete(site_cache)


@receiver(post_save, sender=UserSite)
def index_item(sender, instance, created, **kwargs):
    instance.clear_cache()
