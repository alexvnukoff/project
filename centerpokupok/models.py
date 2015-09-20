from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import HStoreField
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from b24online.custom import CustomImageField
from b24online.models import Company, CURRENCY, AdditionalPage, Gallery, image_storage, IndexedModelMixin, \
    ActiveModelMixing
from b24online.utils import generate_upload_path, reindex_instance


class B2CProductCategory(MPTTModel, IndexedModelMixin):
    name = models.CharField(max_length=255, blank=False, null=False)
    slug = models.SlugField()
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


class B2CProduct(ActiveModelMixing, models.Model, IndexedModelMixin):
    name = models.CharField(max_length=255, blank=False, name=False)
    categories = models.ManyToManyField(B2CProductCategory)
    slug = models.SlugField()
    short_description = models.TextField(null=False)
    description = models.TextField(blank=False, null=False)
    image = CustomImageField(upload_to=generate_upload_path, storage=image_storage, sizes=['big', 'small', 'th'],
                             blank=True, null=True, max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='b2c_products')
    keywords = models.CharField(max_length=2048, blank=True, null=False)
    currency = models.CharField(max_length=255, blank=False, null=True, choices=CURRENCY)
    cost = models.DecimalField(max_digits=15, decimal_places=3, null=True, blank=False)
    galleries = GenericRelation(Gallery)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    additional_pages = GenericRelation(AdditionalPage)
    metadata = HStoreField()

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        index_together = [
            ['is_active', 'is_deleted', 'created_at', 'company'],
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
        return reverse('products:B2CDetail', args=[self.slug, self.pk])


class B2CProductComment(MPTTModel):
    content = models.TextField()
    product = models.ForeignKey(B2CProduct)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


@receiver(post_save, sender=B2CProductCategory)
def initial_department(sender, instance, created, **kwargs):
    instance.reindex()