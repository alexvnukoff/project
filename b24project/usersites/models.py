# -*- coding: utf-8 -*-
import os
import logging
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db import models
from django.utils import timezone
from django.db import transaction, IntegrityError

from b24online.custom import CustomImageField
from b24online.models import (Organization, image_storage, Gallery,
                              ActiveModelMixing, GalleryImage,
                              CURRENCY)
from paypal.standard.ipn.models import PayPalIPN
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
    class Meta:
        verbose_name = "Tempate"
        verbose_name_plural = "Tempates"

    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    thumbnail = CustomImageField(upload_to=generate_upload_path, storage=image_storage, sizes=['big', 'small'], max_length=1000)
    folder_name = models.CharField(max_length=255)
    published = models.BooleanField(default=True)

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


class UserSiteSchemeColor(models.Model):
    class Meta:
        verbose_name = "Scheme color"
        verbose_name_plural = "Scheme colors"

    template = models.ForeignKey(UserSiteTemplate, related_name='colors')
    name = models.CharField(max_length=255)
    folder_name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class UserSite(ActiveModelMixing, models.Model):

    LANG_LIST = [('auto', 'Auto')] + list(settings.LANGUAGES)

    template = models.ForeignKey(ExternalSiteTemplate, blank=True, null=True)
    user_template = models.ForeignKey(UserSiteTemplate, blank=True, null=True)
    color_template = models.ForeignKey(UserSiteSchemeColor, blank=True, null=True)
    organization = models.OneToOneField(Organization, related_name='org_user_site', on_delete=models.CASCADE,)
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
    is_delivery_available = models.BooleanField(default=True)
    delivery_currency = models.CharField(max_length=20, blank=False, 
                                         null=True, choices=CURRENCY)
    delivery_cost = models.DecimalField(max_digits=15, decimal_places=2, 
                                        null=True, blank=False)
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

    @property
    def color(self):
        if self.color_template:
            return {
               'name': self.color_template,
               'path': self.color_template.folder_name,
               }
        return False

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


@receiver(post_save, sender=PayPalIPN)
def add_deal_for_product(sender, instance, created, **kwargs):
    """
    Add Deal for the product from Basket after PayPal success payment. 
    """
    from tpp.DynamicSiteMiddleware import get_current_site
    from centerpokupok.models import B2CProduct
    from b24online.models import (DealOrder, Deal, DealItem)

    if created and instance and instance.item_number:
        try:
            item_id = int(instance.item_number)
            item = B2CProduct.objects.get(id=item_id)
        except (TypeError, B2CProduct.DoesNotExist):
            pass
        else:
            supplier = get_current_site().user_site.organization
            last_name = instance.last_name
            first_name = instance.first_name
            payer_email = instance.payer_email
            try:
                with transaction.atomic():
                    # Deal order
                    deal_order = DealOrder.objects.create(
                        customer_type=DealOrder.AS_PERSON,
                        status=DealOrder.READY,
                        deal_place=DealOrder.ON_USERSITE
                    )
                    deal_order.save()

                    deal = Deal.objects.create(
                        deal_order=deal_order,
                        currency=item.currency,
                        supplier_company=supplier,
                        person_last_name=last_name,
                        person_first_name=first_name,
                        person_email=payer_email,
                        status=Deal.PAID_BY_PAYPAL,
                    )
                    model_type = ContentType.objects.get_for_model(item)
                    deal_item = DealItem.objects.create(
                        deal=deal,
                        content_type=model_type,
                        object_id=item.pk,
                        quantity=1,
                        currency=item.currency,
                        cost=item.cost
                    )
            except IntegrityError:
                raise
