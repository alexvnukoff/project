# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import HStoreField, DateRangeField
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.timezone import now
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from b24online.custom import CustomImageField
from b24online.models import (Company, CURRENCY, AdditionalPage, Gallery, 
                              image_storage, IndexedModelMixin, 
                              ActiveModelMixing, GalleryImage, 
                              Producer)
from b24online.utils import generate_upload_path, reindex_instance
import uuid
from decimal import Decimal


class B2CProductCategory(MPTTModel, IndexedModelMixin):
    name = models.CharField(max_length=255, blank=False, null=False)
    slug = models.SlugField(max_length=255)
    image = CustomImageField(storage=image_storage, blank=True, null=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    @staticmethod
    def get_index_model(**kwargs):
        from b24online.search_indexes import B2cProductCategoryIndex
        return B2cProductCategoryIndex

    def get_absolute_url(self):
        return reverse('b2c_category:detail', args=[self.slug, self.pk])

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class B2CProduct(ActiveModelMixing, models.Model, IndexedModelMixin):
    name = models.CharField(max_length=255, blank=False, name=False)
    categories = models.ManyToManyField(B2CProductCategory, related_name='products')
    slug = models.SlugField(max_length=255)
    short_description = models.TextField(null=False)
    description = models.TextField(blank=False, null=False)
    image = CustomImageField(upload_to=generate_upload_path, storage=image_storage, sizes=['big', 'small', 'th'],
                             blank=True, null=True, max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='b2c_products')
    keywords = models.CharField(max_length=2048, blank=True, null=False)
    currency = models.CharField(max_length=255, blank=False, null=True, choices=CURRENCY)
    cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=False)
    producer = models.ForeignKey(Producer, related_name='b2c_products', 
                                 verbose_name=_('Producer'), 
                                 null=True, blank=True)
    galleries = GenericRelation(Gallery)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    additional_pages = GenericRelation(AdditionalPage)
    metadata = HStoreField()
    discount_percent = models.FloatField(null=True, blank=True)
    coupon_discount_percent = models.FloatField(null=True, blank=True)
    coupon_dates = DateRangeField(null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        index_together = [
            ['created_at', 'company'],
        ]

    def upload_images(self):
        from core import tasks
        params = {
            'file': self.image.path,
            'sizes': {
                'big': {'box': (500, 500), 'fit': False},
                'small': {'box': (200, 200), 'fit': False},
                'th': {'box': (80, 80), 'fit': True}
            }
        }

        tasks.upload_images.delay(params)

    @property
    def country(self):
        return self.company.country

    @property
    def sku(self):
        if self.metadata:
            return self.metadata.get('stock_keeping_unit', None)
        return None

    @staticmethod
    def get_index_model(**kwargs):
        from b24online.search_indexes import B2cProductIndex
        return B2cProductIndex

    def __str__(self):
        return self.name

    def has_perm(self, user):
        return self.company.has_perm(user)

    def get_absolute_url(self):
        return reverse('products:detail', args=[self.slug, self.pk])

    @property
    def gallery_images(self):
        model_type = ContentType.objects.get_for_model(self)
        return GalleryImage.objects.filter(gallery__content_type=model_type, gallery__object_id=self.pk)

    @property
    def start_coupon_date(self):
        if self.coupon_dates:
            return self.coupon_dates.lower
        return None

    @property
    def end_coupon_date(self):
        if self.coupon_dates:
            return self.coupon_dates.upper
        return None

    @property
    def is_coupon(self):
        return self.start_coupon_date and self.end_coupon_date \
               and self.start_coupon_date <= now().date() < self.end_coupon_date

    @property
    def has_discount(self):
        return self.cost and (self.is_coupon or self.discount_percent)

    def get_discount_price(self):
        discount_percent = 0
        original_price = self.cost or 0

        if self.is_coupon:
            discount_percent = self.coupon_discount_percent
        elif self.discount_percent:
            discount_percent = self.discount_percent
        return original_price - original_price * Decimal(discount_percent) / 100

    def get_profit(self):
        return self.cost - self.get_discount_price()

    def has_discount(self):
        return self.is_coupon or self.discount_percent




class B2CProductComment(MPTTModel):
    content = models.TextField()
    product = models.ForeignKey(B2CProduct)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)


@receiver(post_save, sender=B2CProductCategory)
def initial_department(sender, instance, created, **kwargs):
    instance.reindex()


class UserBasket(models.Model):
    class Meta:
        verbose_name = _("Basket")
        verbose_name_plural = _('Baskets')
        ordering = ('-created',)

    user_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site_id = models.IntegerField(_('Site ID'), default=settings.SITE_ID)
    currency = models.CharField(max_length=11, blank=True, null=True)
    paypal = models.CharField(max_length=111, blank=True, null=True)
    created = models.DateTimeField(_('Created'), default=timezone.now)
    checked_out = models.BooleanField(_('Ordered?'), default=False)

    def __str__(self):
        return '{0}'.format(self.user_uuid)


class BasketItem(models.Model):
    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _('Products')
        ordering = ('basket',)

    basket = models.ForeignKey(UserBasket, verbose_name=_('basket'), related_name='items')
    product = models.ForeignKey('B2CProduct', related_name='basket_product')
    quantity = models.PositiveIntegerField(_('Quantity'), default=0)

    def __str__(self):
        return '{0}'.format(self.product_id)
