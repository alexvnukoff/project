from argparse import ArgumentError
import os
from urllib.parse import urljoin
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import HStoreField, DateTimeRangeField, DateRangeField
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils._os import abspathu
from django.utils.translation import ugettext_lazy as _
from guardian.models import UserObjectPermissionBase, GroupObjectPermissionBase
from django.db import transaction

# Create your models here.
from guardian.shortcuts import assign_perm, remove_perm
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from polymorphic_tree.models import PolymorphicMPTTModel, PolymorphicTreeForeignKey
from b24online.custom import CustomImageField, S3ImageStorage, S3FileStorage
from b24online.utils import create_slug, generate_upload_path, reindex_instance
from core import tasks
from core.models import User

CURRENCY = [
    ('NIS', _('Israeli New Sheqel')),
    ('EUR', _('Euro')),
    ('USD', _('Dollar')),
    ('UAH', _('Hryvnia')),
    ('RUB', _('Russian Ruble'))
]

MEASUREMENT_UNITS = [
    ('kg', _('Kilogram')),
    ('pcs', _('Piece'))
]

image_storage = S3ImageStorage()
file_storage = S3FileStorage()


class Advertisement(models.Model):
    pass


class ContextAdvertisement(Advertisement):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    is_active = models.BooleanField(default=True)
    dates = DateTimeRangeField()

    created_by = models.ForeignKey(User, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(User, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def has_perm(self, user):
        return self.item.has_perm(user)

    class Meta:
        index_together = [
            ['content_type', 'is_active'],
        ]


class ContextAdvertisementTarget(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    advertisement_item = models.ForeignKey(ContextAdvertisement, related_name='targets', on_delete=models.CASCADE)

    created_by = models.ForeignKey(User, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(User, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def has_perm(self, user):
        return self.advertisement_item.has_perm(user)


class Gallery(models.Model):
    title = models.CharField(max_length=266, blank=False, null=False)
    is_active = models.BooleanField(default=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')

    created_by = models.ForeignKey(User, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(User, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def has_perm(self, user):
        return self.item.has_perm(user)

    @classmethod
    def create_default_gallery(cls, item, user):
        gallery = cls(title='default', item=item, created_by=user, updated_by=user)
        gallery.save()

        return gallery

    def add_image(self, user, image):
        return GalleryImage.objects.create(image=image, gallery=self, created_by=user, updated_by=user)

    def __str__(self):
        return self.title


class GalleryImage(models.Model):
    gallery = models.ForeignKey(Gallery, related_name='gallery_items')
    image = CustomImageField(storage=image_storage)
    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(User, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(User, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def has_perm(self, user):
        return self.gallery.has_perm(user)


class Document(models.Model):
    description = models.CharField(max_length=255, blank=False, null=False)
    document = models.FileField(storage=file_storage)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(User, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(User, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def has_perm(self, user):
        return self.item.has_perm(user)


class AdditionalPage(models.Model):
    title = models.CharField(max_length=255, blank=False, null=False)
    content = models.TextField(blank=False, null=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(User, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(User, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def has_perm(self, user):
        return self.item.haxs_perm(user)


class Branch(MPTTModel):
    name = models.CharField(max_length=255, blank=False, null=False, db_index=True)
    slug = models.SlugField()
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    is_active = models.BooleanField(default=True)

    @staticmethod
    def get_index_model():
        from b24online.search_indexes import BranchIndex
        return BranchIndex

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('branch:detail', args=[self.slug, self.pk])


class Country(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False, db_index=True)
    flag = models.CharField(max_length=255, blank=False, null=False)
    slug = models.SlugField()

    @staticmethod
    def get_index_model():
        from b24online.search_indexes import CountryIndex
        return CountryIndex

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('country:detail', args=[self.slug, self.pk])


class Organization(PolymorphicMPTTModel):
    countries = models.ManyToManyField(Country, related_name='organizations')
    parent = PolymorphicTreeForeignKey('self', blank=True, null=True, related_name='children',
                                       verbose_name=_('parent'), db_index=True)
    context_advertisements = GenericRelation(ContextAdvertisement)
    is_active = models.BooleanField(default=True)

    def has_perm(self, user):
        if user is None or not user.is_authenticated() or user.is_anonymous():
            return False

        if user.is_superuser or user.is_commando:
            return True

        return self.pk in user.manageable_organizations()

    def create_department(self, name, user):
        return Department.objects.create(
            name=name,
            created_by=user,
            updated_by=user,
            organization=self
        )

    def create_vacancy(self, name, department, user):
        if department.organization != self:
            raise ArgumentError('department', 'Unknown department')

        return department.create_vacancy(name, user)

    @property
    def vacancies(self):
        return Vacancy.objects.filter(department__organization=self)

    class Meta:
        permissions = (
            ('manage_organization', 'Manage Organization'),
        )


class ProjectUserObjectPermission(UserObjectPermissionBase):
    content_object = models.ForeignKey(Organization)


class ProjectGroupObjectPermission(GroupObjectPermissionBase):
    content_object = models.ForeignKey(Organization)


class Chamber(Organization):
    CHAMBER_TYPES = [
        ('international', _('International')),
        ('national', _('National')),
        ('affiliate', _('Affiliate')),
    ]

    name = models.CharField(max_length=255, blank=False, null=False, db_index=True)
    slug = models.SlugField()
    short_description = models.TextField(null=False, blank=True)
    description = models.TextField(null=False, blank=False)
    logo = CustomImageField(upload_to=generate_upload_path, storage=image_storage,
                            sizes=['big', 'small', 'th'], max_length=255)
    keywords = models.CharField(max_length=2048, blank=True, null=False)
    director = models.CharField(max_length=255, blank=True, null=False)
    address = models.CharField(max_length=2048, blank=True, null=False)
    org_type = models.CharField(max_length=30, choices=CHAMBER_TYPES, blank=False, null=False)
    metadata = HStoreField()
    additional_pages = GenericRelation(AdditionalPage)
    galleries = GenericRelation(Gallery)

    created_by = models.ForeignKey(User, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(User, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def upload_images(self, changed_data=None):
        params = []

        if (changed_data is None or 'logo' in changed_data) and self.logo:
            params.append({
                'file': self.logo.path,
                'sizes': {
                    'big': {'box': (500, 500), 'fit': False},
                    'small': {'box': (200, 200), 'fit': False},
                    'th': {'box': (80, 80), 'fit': True}
                }
            })

        if (changed_data is None or 'flag' in changed_data) and self.flag:
            params.append({
                'file': (os.path.join(abspathu(settings.MEDIA_ROOT), self.flag)).replace('\\', '/'),
                'sizes': {
                    'small': {'box': (20, 15), 'fit': True},
                }
            })

        tasks.upload_images.delay(*params)

    def reindex(self):
        reindex_instance(self)

    @property
    def country(self):
        # cache_name = "%s:%s" % (Chamber.cache_prefix(), 'country')
        # cached = cache.get(cache_name)

        if self.org_type == 'international':
            return None
            # raise ValueError('International organization')

        chamber = self.get_root() if self.org_type == 'affiliate' else self
        countries = chamber.countries.all()

        if len(countries) > 1:
            raise ValueError('Not international chamber have more than one country')

        if len(countries) == 0:
            raise ValueError("Can not find country for chambers: (%s, %s)" % (self.pk, chamber.pk))

        return countries[0]

    @property
    def flag(self):
        if self.metadata:
            return self.metadata.get('flag', '')

        return None

    @property
    def flag_url(self):
        if self.flag:
            path = "small/%s" % self.flag
            return urljoin(settings.MEDIA_URL, path)

        return self.flag

    @property
    def phone(self):
        if self.metadata:
            return self.metadata.get('phone', '')

        return None

    @property
    def fax(self):
        if self.metadata:
            return self.metadata.get('fax', '')

        return None

    @property
    def site(self):
        if self.metadata:
            return self.metadata.get('site', '')

        return None

    @property
    def detail_url(self):  # Deprecated
        return self.get_absolute_url()

    def get_absolute_url(self):
        return reverse('tpp:detail', args=[self.slug, self.pk])

    @property
    def location(self):
        if self.metadata:
            return self.metadata.get('location', '')

        return None

    @property
    def email(self):
        if self.metadata:
            return self.metadata.get('email', '')

        return None

    @property
    def vatin(self):
        if self.metadata:
            return self.metadata.get('vat_identification_number', '')

        return None

    @classmethod
    def cache_prefix(cls):
        return cls.__name__

    @staticmethod
    def get_index_model():
        from b24online.search_indexes import ChamberIndex
        return ChamberIndex

    def __str__(self):
        return self.name


class Company(Organization):
    name = models.CharField(max_length=255, blank=False, null=False)
    slug = models.SlugField()
    short_description = models.TextField(null=False, blank=True)
    description = models.TextField(null=False, blank=False)
    logo = CustomImageField(upload_to=generate_upload_path, storage=image_storage,
                            sizes=['big', 'small', 'th'], max_length=255)
    keywords = models.CharField(max_length=2048, blank=True, null=False)
    director = models.CharField(max_length=255, blank=True, null=False)
    address = models.CharField(max_length=2048, blank=True, null=False)
    slogan = models.CharField(max_length=2048, blank=True, null=False)
    metadata = HStoreField()
    branches = models.ManyToManyField(Branch)
    additional_pages = GenericRelation(AdditionalPage)
    galleries = GenericRelation(Gallery)

    created_by = models.ForeignKey(User, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(User, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def upload_images(self):
        params = {
            'file': self.logo.path,
            'sizes': {
                'big': {'box': (500, 500), 'fit': False},
                'small': {'box': (200, 200), 'fit': False},
                'th': {'box': (80, 80), 'fit': True}
            }
        }

        tasks.upload_images.delay(params)

    def reindex(self):
        reindex_instance(self)

    @property
    def country(self):
        countries = self.countries.all()

        if len(countries) > 1:
            # TODO what to do here?
            raise ValueError('Company related to more than one country')

        if len(countries) == 0:
            raise ValueError('Company do not have country')

        return countries[0]

    def get_absolute_url(self):
        return reverse('companies:detail', args=[self.slug, self.pk])

    @property
    def detail_url(self):
        return self.get_absolute_url()

    @property
    def phone(self):
        if self.metadata:
            return self.metadata.get('phone', '')

        return None

    @property
    def fax(self):
        if self.metadata:
            return self.metadata.get('fax', '')

        return None

    @property
    def site(self):
        if self.metadata:
            return self.metadata.get('site', '')

        return None

    @property
    def location(self):
        if self.metadata:
            return self.metadata.get('location', '')

        return None

    @property
    def email(self):
        if self.metadata:
            return self.metadata.get('email', None)

        return None

    @property
    def vatin(self):
        if self.metadata:
            return self.metadata.get('vat_identification_number', '')

        return None

    @staticmethod
    def get_index_model():
        from b24online.search_indexes import CompanyIndex
        return CompanyIndex

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False, db_index=True)
    slug = models.SlugField()
    organization = models.ForeignKey(Organization, db_index=True, related_name='departments')
    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(User, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(User, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def has_perm(self, user):
        return self.organization.has_perm(user)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('department:detail', args=[self.slug, self.pk])

    def create_vacancy(self, name, user):
        return Vacancy.objects.create(
            name=name,
            created_by=user,
            updated_by=user,
            department=self
        )


class Vacancy(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False, db_index=True)
    slug = models.SlugField()
    department = models.ForeignKey(Department, related_name='vacancies', db_index=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, related_name='work_positions')
    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(User, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(User, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def has_perm(self, user):
        return self.department.has_perm(user)

    def assign_employee(self, user, is_admin):
        if self.user:
            raise ValueError('Employee already exists')

        if user.work_positions.filter(department__organization=self.department.organization).exists():
            raise ValueError('Employee already exists in organization')

        with transaction.atomic():
            self.user = user
            self.save()

            if is_admin:
                assign_perm('manage_organization', user, self.department.organization)

    def remove_employee(self):
        with transaction.atomic():
            if self.has_perm(self.user):
                remove_perm('manage_organization', self.user, self.department.organization)

            self.user = None
            self.save()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('vacancy:detail', args=[self.slug, self.pk])


class BusinessProposalCategory(MPTTModel):
    name = models.CharField(max_length=255, blank=False, null=False, db_index=True)
    slug = models.SlugField()
    is_active = models.BooleanField(default=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    @staticmethod
    def get_index_model():
        from b24online.search_indexes import BusinessProposalCategoryIndex
        return BusinessProposalCategoryIndex

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('bp_category:detail', args=[self.slug, self.pk])


class BusinessProposal(models.Model):
    title = models.CharField(max_length=255, blank=False, null=False)
    slug = models.SlugField()
    description = models.TextField(blank=False, null=False)
    keywords = models.CharField(max_length=2048, blank=True, null=False)
    additional_pages = GenericRelation(AdditionalPage)
    documents = GenericRelation(Document)
    branches = models.ManyToManyField(Branch)
    galleries = GenericRelation(Gallery)
    country = models.ForeignKey(Country)
    is_active = models.BooleanField(default=True)
    categories = models.ManyToManyField(BusinessProposalCategory)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    context_advertisements = GenericRelation(ContextAdvertisement)

    created_by = models.ForeignKey(User, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(User, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def has_perm(self, user):
        return self.organization.has_perm(user)

    @staticmethod
    def get_index_model():
        from b24online.search_indexes import BusinessProposalIndex
        return BusinessProposalIndex

    def reindex(self):
        reindex_instance(self)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('proposal:detail', args=[self.slug, self.pk])


class InnovationProject(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    slug = models.SlugField()
    description = models.TextField(blank=False, null=False)
    product_name = models.CharField(max_length=255, blank=False, null=False)
    business_plan = models.TextField(blank=False, null=False)
    documents = GenericRelation(Document)
    currency = models.CharField(max_length=255, blank=False, null=True, choices=CURRENCY)
    cost = models.DecimalField(max_digits=15, decimal_places=3, null=True, blank=False)
    organization = models.ForeignKey(Organization, null=True, on_delete=models.CASCADE)
    branches = models.ManyToManyField(Branch)
    metadata = HStoreField()
    keywords = models.CharField(max_length=2048, blank=True, null=False)
    galleries = GenericRelation(Gallery)
    is_active = models.BooleanField(default=True)
    additional_pages = GenericRelation(AdditionalPage)
    context_advertisements = GenericRelation(ContextAdvertisement)

    created_by = models.ForeignKey(User, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(User, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def has_perm(self, user):
        if self.organization:
            return self.organization.has_perm(user)

        return user.is_superuser or user.is_commando or self.created_by == user

    @property
    def country(self):
        if self.organization:
            return self.organization.country
        else:
            return self.created_by.profile.country

    @property
    def release_date(self):
        if self.metadata:
            return self.metadata.get('release_date', None)

        return None

    @property
    def site(self):
        if self.metadata:
            return self.metadata.get('site', None)

        return None

    @staticmethod
    def get_index_model():
        from b24online.search_indexes import InnovationProjectIndex
        return InnovationProjectIndex

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('innov:detail', args=[self.slug, self.pk])

    def reindex(self):
        reindex_instance(self)


class B2BProductCategory(MPTTModel):
    name = models.CharField(max_length=255, blank=False, null=False, db_index=True)
    slug = models.SlugField()
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    image = CustomImageField(storage=image_storage, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    @staticmethod
    def get_index_model():
        from b24online.search_indexes import B2bProductCategoryIndex
        return B2bProductCategoryIndex

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('b2b_category:detail', args=[self.slug, self.pk])


class B2BProduct(models.Model):
    name = models.CharField(max_length=255, blank=False, name=False)
    slug = models.SlugField()
    short_description = models.TextField(null=False)
    description = models.TextField(blank=False, null=False)
    image = CustomImageField(upload_to=generate_upload_path, storage=image_storage, sizes=['big', 'small', 'th'],
                             blank=True, null=True, max_length=255)
    categories = models.ManyToManyField(B2BProductCategory)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    keywords = models.CharField(max_length=2048, blank=True, null=False)
    currency = models.CharField(max_length=255, blank=True, null=True, choices=CURRENCY)
    measurement_unit = models.CharField(max_length=255, blank=True, null=True, choices=MEASUREMENT_UNITS)
    cost = models.DecimalField(max_digits=15, decimal_places=3, null=True, blank=True)
    documents = GenericRelation(Document)
    galleries = GenericRelation(Gallery)
    branches = models.ManyToManyField(Branch)
    is_active = models.BooleanField(default=True)
    additional_pages = GenericRelation(AdditionalPage)
    metadata = HStoreField()
    context_advertisements = GenericRelation(ContextAdvertisement)

    created_by = models.ForeignKey(User, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(User, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def upload_images(self):
        params = {
            'file': self.image.path,
            'sizes': {
                'big': {'box': (500, 500), 'fit': False},
                'small': {'box': (200, 200), 'fit': False},
                'th': {'box': (80, 80), 'fit': True}
            }
        }

        tasks.upload_images.delay(params)

    def reindex(self):
        reindex_instance(self)

    @property
    def country(self):
        return self.company.country

    @property
    def sku(self):
        if self.metadata:
            return self.metadata.get('stock_keeping_unit', None)

        return None

    def __str__(self):
        return self.name

    @staticmethod
    def get_index_model():
        from b24online.search_indexes import B2BProductIndex
        return B2BProductIndex

    def has_perm(self, user):
        return self.company.has_perm(user)

    def get_absolute_url(self):
        return reverse('products:detail', args=[self.slug, self.pk])


class B2BProductComment(MPTTModel):
    content = models.TextField()
    product = models.ForeignKey(B2BProduct, on_delete=models.CASCADE)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(User, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(User, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def has_perm(self, user):
        return user.is_commando or user.is_superuser or self.created_by == user


class NewsCategory(MPTTModel):
    name = models.CharField(max_length=255, blank=False, null=False, db_index=True)
    image = CustomImageField(storage=image_storage, blank=True, null=True)
    slug = models.SlugField()
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    is_active = models.BooleanField(default=True)

    @staticmethod
    def get_index_model():
        from b24online.search_indexes import NewsCategoryIndex
        return NewsCategoryIndex

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('news_category:detail', args=[self.slug, self.pk])


class Greeting(models.Model):
    photo = models.CharField(max_length=255, blank=False, null=False)
    organization = models.CharField(max_length=255, blank=False, null=False)
    name = models.CharField(max_length=255, blank=False, null=False)
    slug = models.SlugField()
    position = models.CharField(max_length=255, blank=False, null=False)
    content = models.TextField(blank=False, null=False)
    is_active = models.BooleanField(default=True)

    @staticmethod
    def get_index_model():
        from b24online.search_indexes import GreetingIndex
        return GreetingIndex

    def __str__(self):
        return self.name

    def has_perm(self, user):
        return user.is_superuser or user.is_commando

    def get_absolute_url(self):
        return reverse('greetings:detail', args=[self.slug, self.pk])


class News(models.Model):
    title = models.CharField(max_length=255, blank=False, null=False)
    image = CustomImageField(upload_to=generate_upload_path, storage=image_storage,
                             sizes=['big', 'small', 'th'], max_length=255, blank=True)
    slug = models.SlugField()
    short_description = models.TextField()
    content = models.TextField()
    is_tv = models.BooleanField(default=False)
    categories = models.ManyToManyField(NewsCategory)
    galleries = GenericRelation(Gallery)
    video_code = models.CharField(max_length=255, blank=True, null=False)
    keywords = models.CharField(max_length=2048, blank=True, null=False)
    is_active = models.BooleanField(default=True)
    organization = models.ForeignKey(Organization, null=True, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, null=True)
    context_advertisements = GenericRelation(ContextAdvertisement)

    created_by = models.ForeignKey(User, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(User, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def upload_images(self):
        params = {
            'file': self.image.path,
            'sizes': {
                'big': {'box': (500, 500), 'fit': False},
                'small': {'box': (200, 200), 'fit': False},
                'th': {'box': (80, 80), 'fit': True}
            }
        }

        tasks.upload_images.delay(params)

    @staticmethod
    def get_index_model():
        from b24online.search_indexes import NewsIndex
        return NewsIndex

    def reindex(self):
        reindex_instance(self)

    def __str__(self):
        return self.title

    def has_perm(self, user):
        if self.organization:
            return self.organization.has_perm(user)

        return user.is_commando or user.is_superuser

    def get_absolute_url(self):
        if self.is_tv:
            return reverse('tv:detail', args=[self.slug, self.pk])

        return reverse('news:detail', args=[self.slug, self.pk])


class Tender(models.Model):
    title = models.CharField(max_length=255, blank=False, null=False)
    slug = models.SlugField()
    content = models.TextField(blank=False, null=False)
    currency = models.CharField(max_length=255, blank=False, null=True, choices=CURRENCY)
    cost = models.DecimalField(max_digits=15, decimal_places=3, null=True, blank=False)
    branches = models.ManyToManyField(Branch)
    documents = GenericRelation(Document)
    keywords = models.CharField(max_length=2048, blank=True, null=False)
    dates = DateRangeField(null=True)
    is_active = models.BooleanField(default=True)
    additional_pages = GenericRelation(AdditionalPage)
    country = models.ForeignKey(Country)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    created_by = models.ForeignKey(User, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(User, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def start_date(self):
        if self.dates:
            return self.dates.lower

        return None

    @property
    def end_date(self):
        if self.dates:
            return self.dates.upper

        return None

    def __str__(self):
        return self.title

    @staticmethod
    def get_index_model():
        from b24online.search_indexes import TenderIndex
        return TenderIndex

    def has_perm(self, user):
        return self.organization.has_perm(user)

    def get_absolute_url(self):
        return reverse('tenders:detail', args=[self.slug, self.pk])

    def reindex(self):
        reindex_instance(self)


class Profile(models.Model):
    first_name = models.CharField(max_length=255, blank=False, null=False)
    middle_name = models.CharField(max_length=255, blank=True, null=False)
    last_name = models.CharField(max_length=255, blank=True, null=False)
    avatar = models.CharField(max_length=255, blank=True, null=False)
    mobile_number = models.CharField(max_length=255, blank=True, null=False)
    site = models.CharField(max_length=255, blank=True, null=False)
    profession = models.CharField(max_length=255, blank=True, null=False)
    country = models.ForeignKey(Country)
    birthday = models.DateField()
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)

    GENDERS = [('Male', _('Male')), ('Female', _('Female'))]
    sex = models.CharField(max_length=255, blank=False, null=True, choices=GENDERS)

    TYPES = [('Businessman', _('Businessman')), ('Individual', _('Individual'))]
    user_type = models.CharField(max_length=255, blank=False, null=False, choices=TYPES)

    @property
    def full_name(self):
        return "%s %s %s" % (self.first_name, self.middle_name, self.last_name)

    @staticmethod
    def get_index_model():
        from b24online.search_indexes import ProfileIndex
        return ProfileIndex

    def __str__(self):
        return self.full_name

    def has_perm(self, user):
        return user.is_commando or user.is_superuser or self.user == user


class Exhibition(models.Model):
    title = models.CharField(max_length=255, blank=False, null=False)
    slug = models.SlugField()
    description = models.TextField(blank=False, null=False)
    documents = GenericRelation(Document)
    keywords = models.CharField(max_length=2048, blank=True, null=False)
    dates = DateRangeField(null=True)
    city = models.CharField(max_length=255, blank=False, null=True)
    route = models.CharField(blank=True, null=False, max_length=1024)
    is_active = models.BooleanField(default=True)
    country = models.ForeignKey(Country)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    additional_pages = GenericRelation(AdditionalPage)
    context_advertisements = GenericRelation(ContextAdvertisement)
    branches = models.ManyToManyField(Branch)
    metadata = HStoreField()

    created_by = models.ForeignKey(User, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(User, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def start_date(self):
        if self.dates:
            return self.dates.lower

        return None

    @property
    def end_date(self):
        if self.dates:
            return self.dates.upper

        return None

    @property
    def location(self):
        if self.metadata:
            return self.metadata.get('location', '')

        return None

    def reindex(self):
        reindex_instance(self)

    @staticmethod
    def get_index_model():
        from b24online.search_indexes import ExhibitionIndex
        return ExhibitionIndex

    def __str__(self):
        return self.title

    def has_perm(self, user):
        return self.organization.has_perm(user)

    def get_absolute_url(self):
        return reverse('exhibitions:detail', args=[self.slug, self.pk])


class StaticPage(models.Model):
    title = models.CharField(max_length=255, blank=False, null=False)
    slug = models.SlugField()
    content = models.TextField(blank=False, null=False)
    is_on_top = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    SITE_TYPES = [
        ('b2b', _('B2B')),
        ('b2c', _('B2C')),
        ('user_site', _('User sites'))
    ]

    site_type = models.CharField(max_length=10, choices=SITE_TYPES)

    PAGE_TYPES = (
        ('about', 'About'),
        ('advices', 'Advices'),
        ('contacts', 'Contacts'),
        ('buyer', 'To buyer'),
        ('seller', 'To seller'),
    )

    page_type = models.CharField(max_length=200, choices=PAGE_TYPES)

    def __str__(self):
        return self.title

    def has_perm(self, user):
        return user.is_commando or user.is_superuser

    def get_absolute_url(self):
        return reverse('project:detail', args=[self.slug, self.pk])

    class Meta:
        index_together = [
            ['page_type', 'site_type'],
        ]


class Notification(models.Model):
    user = models.ForeignKey(User, related_name="notifications")
    read = models.BooleanField(default=False)
    message = models.CharField(max_length=1024, blank=False, null=False)

    MESSAGE_TYPE = (
        ('item_creating', 'Creating item in process'),
        ('item_updating', 'Update item in process'),
        ('item_created', 'Item created'),
        ('item_updated', 'Item Updated'),
        ("error_creating", "Error in creating"))

    type = models.CharField(max_length=200, choices=MESSAGE_TYPE)

    def __str__(self):
        return self.message


class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent')
    recipient = models.ForeignKey(User, related_name='received')
    is_read = models.BooleanField(default=False)
    content = models.TextField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        index_together = [
            ['recipient', 'sender'],
        ]

    @classmethod
    def add_message(cls, content, sender, recipient_id, notify=True):
        with transaction.atomic():
            recipient = User.objects.get(pk=recipient_id)
            cls.objects.create(sender=sender, content=content, recipient=recipient)

        if notify:
            from appl import func
            func.publish_realtime('private_massage', recipient=recipient_id, fromUser=sender.pk)

    def __str__(self):
        return "From %s to %s at %s" % (self.sender.profile, self.recipient.profile, self.sent_at)


class BannerBlock(models.Model):
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    image = CustomImageField(storage=image_storage, null=True)
    description = models.CharField(max_length=1024)
    factor = models.FloatField(default=1)

    BLOCK_TYPES = [
        ('b2b', _('B2B')),
        ('b2c', _('B2C')),
        ('user_site', _('User sites'))
    ]

    block_type = models.CharField(max_length=10, choices=BLOCK_TYPES)

    def get_absolute_url(self):
        return reverse('adv_banners:banner_form', args=[self.pk])

    class Meta:
        index_together = [
            ['code', 'block_type'],
        ]


class Banner(Advertisement):
    title = models.CharField(max_length=255)
    link = models.URLField()
    image = CustomImageField(storage=image_storage)
    block = models.ForeignKey(BannerBlock)
    organization = models.ForeignKey(Organization, null=True, on_delete=models.CASCADE)
    dates = DateTimeRangeField()
    is_active = models.BooleanField(default=True)
    site = models.ForeignKey(Site)

    created_by = models.ForeignKey(User, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(User, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def has_perm(self, user):
        if self.organization:
            return self.organization.has_perm(user)

        return user.is_superuser or user.is_commando or self.created_by == user


class BannerTarget(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    banner = models.ForeignKey(Banner, related_name='targets', on_delete=models.CASCADE)

    created_by = models.ForeignKey(User, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(User, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def has_perm(self, user):
        return self.banner.has_perm(user)


class AdvertisementPrices(models.Model):
    ADVERTISEMENT_TYPES = [('banner', _('Banners')), ('context', _('Context Advertisement'))]

    advertisement_type = models.CharField(max_length=10, choices=ADVERTISEMENT_TYPES)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    valid_from = models.DateTimeField(auto_now_add=True)
    valid_to = models.DateTimeField()
    price = models.DecimalField(max_digits=15, decimal_places=3, null=False, blank=False)

    created_by = models.ForeignKey(User, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(User, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        unique_together = ("content_type", "object_id")


@receiver(pre_save)
def slugify(sender, instance, **kwargs):
    fields = [field.name for field in sender._meta.get_fields()]

    if 'slug' in fields:
        if 'title' in fields:
            string = instance.title
        elif 'name' in fields:
            string = instance.name
        else:
            raise NotImplementedError('Unknown source field for slug')

        instance.slug = create_slug(string)


@receiver(post_save, sender=Company)
@receiver(post_save, sender=Chamber)
def initial_department(sender, instance, created, **kwargs):
    if not instance.created_by.is_superuser and not instance.created_by.is_commando and created:
        department = instance.create_department(_('Administration'), instance.created_by)
        vacancy = instance.create_vacancy(_('Admin'), department, instance.created_by)
        vacancy.assign_employee(instance.created_by, True)
