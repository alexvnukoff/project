from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import HStoreField
from django.core.urlresolvers import reverse
from django.db import models
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from b24online.models import Company, CURRENCY, AdditionalPages, Gallery
from core.models import User


class B2CProductCategory(MPTTModel):
    name = models.CharField(max_length=255, blank=False, null=False)
    slug = models.SlugField()
    image = models.ImageField(blank=True, null=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    @staticmethod
    def get_index_model():
        from b24online.search_indexes import B2cProductCategoryIndex
        return B2cProductCategoryIndex

    def get_absolute_url(self):
        full_slug = "%s-%s" % (self.slug, self.pk)
        return reverse('b2c_category:detail', kwargs={'slug': full_slug})

    def __str__(self):
        return self.name


class B2CProduct(models.Model):
    name = models.CharField(max_length=255, blank=False, name=False)
    categories = models.ManyToManyField(B2CProductCategory)
    slug = models.SlugField()
    short_description = models.TextField(null=False)
    description = models.TextField(blank=False, null=False)
    image = models.ImageField(blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    keywords = models.CharField(max_length=2048, blank=True, null=False)
    currency = models.CharField(max_length=255, blank=False, null=True, choices=CURRENCY)
    cost = models.DecimalField(max_digits=15, decimal_places=3, null=True, blank=False)
    galleries = GenericRelation(Gallery)
    is_active = models.BooleanField(default=True, db_index=True)
    additional_pages = GenericRelation(AdditionalPages)
    metadata = HStoreField()

    created_by = models.ForeignKey(User, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(User, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def country(self):
        return self.company.country

    @property
    def sku(self):
        return self.metadata.get('stock_keeping_unit', None)

    @staticmethod
    def get_index_model():
        from b24online.search_indexes import B2cProductIndex
        return B2cProductIndex

    def __str__(self):
        return self.name

    def has_perm(self, user):
        return self.company.has_perm(user)

    def get_absolute_url(self):
        full_slug = "%s-%s" % (self.slug, self.pk)
        return reverse('products:detail', kwargs={'slug': full_slug})


class B2CProductComment(MPTTModel):
    content = models.TextField()
    product = models.ForeignKey(B2CProduct)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    created_by = models.ForeignKey(User, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(User, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
