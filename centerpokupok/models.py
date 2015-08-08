from django.db import models
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from b24online.models import Company
from core.models import User


class B2CProductCategory(MPTTModel):
    name = models.CharField(max_length=255, blank=False, null=False)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    def __str__(self):
        return self.name


class B2CProduct(models.Model):
    name = models.CharField(max_length=255, blank=False, name=False)
    categories = models.ManyToManyField(B2CProductCategory)
    company = models.ForeignKey(Company)
    is_active = models.BooleanField(default=True, db_index=True)

    created_by = models.ForeignKey(User, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(User, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class B2CProductComment(MPTTModel):
    product = models.ForeignKey(B2CProduct)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    created_by = models.ForeignKey(User, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(User, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
