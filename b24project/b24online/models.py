# -*- encoding: utf-8 -*-

import os
import datetime
import hashlib
import logging

from argparse import ArgumentError
from urllib.parse import urljoin

from django.conf import settings
from django.utils.functional import curry
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, Group, Permission
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import (HStoreField, DateRangeField,
    DateTimeRangeField, JSONField)
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.core.validators import MinLengthValidator
from django.db import models, transaction
from django.db.models import Q, F, Sum
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils._os import abspathu
from django.utils.encoding import smart_str
from django.utils.translation import ugettext, ugettext_lazy as _
from guardian.models import UserObjectPermissionBase, GroupObjectPermissionBase
from guardian.shortcuts import assign_perm, remove_perm, get_objects_for_user
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from polymorphic_tree.models import PolymorphicMPTTModel, PolymorphicTreeForeignKey
from registration.signals import user_registered
from uuslug import uuslug
from b24online.custom import (CustomImageField, S3ImageStorage, S3FileStorage,
                              LocalFileStorage)
from b24online.utils import (generate_upload_path, reindex_instance,
                             document_upload_path, get_current_organization)
from tpp.celery import app

CURRENCY = [
    ('ILS', _('Israeli New Sheqel')),
    ('EUR', _('Euro')),
    ('USD', _('Dollar')),
    ('UAH', _('Hryvnia')),
    ('RUB', _('Russian Ruble')),
    ('BGN', _('Bulgarian Lev')),
    ('BYR', _('Belarusian Ruble'))
]

MEASUREMENT_UNITS = [
    ('kg', _('Kilogram')),
    ('pcs', _('Piece'))
]

image_storage = S3ImageStorage() \
    if not getattr(settings, 'STORE_FILES_LOCAL', False) \
        else LocalFileStorage()
file_storage = S3ImageStorage() \
    if not getattr(settings, 'STORE_FILES_LOCAL', False) \
        else LocalFileStorage()

logger = logging.getLogger(__name__)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email).lower()
        user = self.model(email=email)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, **extra_fields):
        user = self.create_user(email, password, **extra_fields)
        user.is_active = True
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='E-mail', max_length=255, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)  # for enterprise content management
    is_commando = models.BooleanField(default=False)  # for special purposes
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        return '%s %s' % (self.first_name, self.last_name,)

    def get_short_name(self):
        return self.email

    def __str__(self):
        return self.email

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    def manageable_organizations(self):
        key = "user:%s:manageable_organizations" % self.pk
        organization_ids = cache.get(key)

        if organization_ids is None:
            organization_ids = [org.pk for org in
                                get_objects_for_user(self, 'b24online.manage_organization', Organization)]
            cache.set(key, organization_ids, 60 * 10)

        return organization_ids or []

    class Meta:
        db_table = 'core_user'


class ActiveModelMixing:
    fields_cache = {}

    @classmethod
    def get_active_objects(cls):
        if not cls.fields_cache:
            fields = [field.name for field in cls._meta.get_fields()]
            cls.fields_cache = fields

        filter_args = {}

        if 'is_active' in cls.fields_cache:
            filter_args['is_active'] = True

        if 'is_deleted' in cls.fields_cache:
            filter_args['is_deleted'] = False

        if filter_args:
            return cls.objects.filter(**filter_args)

        return cls.objects.all()


class IndexedModelMixin:
    def reindex(self, is_active_changed=False, *args, **kwargs):
        reindex_instance(self)

    @staticmethod
    def get_index_model(*args, **kwargs):
        raise NotImplementedError('Reindex not implemented')


class AbstractRegisterInfoModel(models.Model):
    """
    The abstract model-container of registration info fields.
    """
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
        verbose_name=_('Creator'), 
        related_name='%(class)s_create_user',
        null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,
        verbose_name=_('Editor'),
        related_name='%(class)s_update_user',
        null=True, blank=True)
    created_at = models.DateTimeField(_('Creation time'),
        default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(_('Update time'),
        auto_now=True, null=True)

    class Meta:
        abstract = True

    @property    
    def created(self):
        """
        Return the created_at datetime text by selected format.
        """
        return self.created_at.strftime('%d/%m/%Y %H:%I:%S')


class AdvertisementPrice(models.Model):
    ADVERTISEMENT_TYPES = [('banner', _('Banners')), ('context', _('Context Advertisement'))]

    advertisement_type = models.CharField(max_length=10, choices=ADVERTISEMENT_TYPES)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    dates = DateTimeRangeField()
    price = models.DecimalField(max_digits=15, decimal_places=2, null=False, blank=False)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("content_type", "object_id")


class Order(models.Model):
    pass


class Advertisement(models.Model):
    dates = DateRangeField()

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


class ContextAdvertisement(ActiveModelMixing, Advertisement):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def has_perm(self, user):
        return self.item.has_perm(user)


class AdvertisementTarget(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    advertisement_item = models.ForeignKey(Advertisement, related_name='targets', on_delete=models.CASCADE)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def has_perm(self, user):
        return self.advertisement_item.has_perm(user)


class Gallery(ActiveModelMixing, models.Model):
    title = models.CharField(max_length=266, blank=False, null=True)
    is_deleted = models.BooleanField(default=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey()

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(default=timezone.now)
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
    image = CustomImageField(upload_to=generate_upload_path, storage=image_storage,
                             sizes=['big', 'small', 'th'], max_length=255)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def has_perm(self, user):
        return self.gallery.has_perm(user)


class Document(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.CharField(max_length=255, blank=False, null=False)
    document = models.FileField(upload_to=document_upload_path)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def has_perm(self, user):
        return self.item.has_perm(user)


class AdditionalPage(models.Model):
    title = models.CharField(max_length=255, blank=False, null=False)
    slug = models.SlugField(max_length=255)
    content = models.TextField(blank=False, null=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def has_perm(self, user):
        return self.item.haxs_perm(user)

    def get_absolute_url(self):
        return reverse('pages:detail', args=[self.slug, self.pk])


class Branch(MPTTModel, IndexedModelMixin):
    name = models.CharField(max_length=255, blank=False, null=False)
    slug = models.SlugField(max_length=255)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    prices = GenericRelation(AdvertisementPrice)

    @staticmethod
    def get_index_model(**kwargs):
        from b24online.search_indexes import BranchIndex
        return BranchIndex

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('branch:detail', args=[self.slug, self.pk])


class Country(models.Model, IndexedModelMixin):
    name = models.CharField(max_length=255, blank=False, null=False)
    flag = models.CharField(max_length=255, blank=False, null=False)
    slug = models.SlugField(max_length=255)
    prices = GenericRelation(AdvertisementPrice)

    @staticmethod
    def get_index_model(**kwargs):
        from b24online.search_indexes import CountryIndex
        return CountryIndex

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('country:detail', args=[self.slug, self.pk])


class Organization(ActiveModelMixing, PolymorphicMPTTModel):
    countries = models.ManyToManyField(Country, related_name='organizations')
    parent = PolymorphicTreeForeignKey('self', blank=True, null=True, related_name='children',
                                       verbose_name=_('parent'), db_index=True)
    context_advertisements = GenericRelation(ContextAdvertisement)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.pk

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

    def create_vacancy(self, name, department, user, **kwargs):
        if department.organization != self:
            raise ArgumentError('department', 'Unknown department')

        return department.create_vacancy(name, user, **kwargs)

    def get_descendants_filtered(self, **filters):
        """
        Return the qs for node descendants under some filtered conditions.
        """
        return self.get_descendants().filter(**filters)

    def get_descendants_for_model(self, model_klass):
        """
        Return the qs for node descendants of defined ContentType.
        """
        assert issubclass(model_klass, models.Model), \
            _('Invalid parameter. Must be a "Model" subclass')
        content_type = ContentType.objects.get_for_model(model_klass) 
        return self.get_descendants().instance_of(model_klass)

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


class Chamber(Organization, IndexedModelMixin):
    CHAMBER_TYPES = [
        ('international', _('International')),
        ('national', _('National')),
        ('affiliate', _('Affiliate')),
    ]

    name = models.CharField(max_length=255, blank=False, null=False)
    slug = models.SlugField(max_length=255)
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
    documents = GenericRelation(Document)
    prices = GenericRelation(AdvertisementPrice)

    def upload_images(self, changed_data=None):
        from core import tasks
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

    def reindex(self, is_active_changed=False, **kwargs):
        from core import tasks
        reindex_instance(self)

        if is_active_changed:
            task_id = 'chamber:on_company_active_changed:%s' % self.pk
            app.control.revoke(task_id)
            tasks.on_chamber_active_changed.apply_async((self.pk,), tasks_id=task_id)

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
            return None  # raise ValueError("Can not find country for chambers: (%s, %s)" % (self.pk, chamber.pk))

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
    def get_index_model(**kwargs):
        from b24online.search_indexes import ChamberIndex
        return ChamberIndex

    @property
    def gallery_images(self):
        model_type = ContentType.objects.get_for_model(self)
        return GalleryImage.objects.filter(gallery__content_type=model_type, gallery__object_id=self.pk)

    def __str__(self):
        return self.name


class Company(Organization, IndexedModelMixin):
    name = models.CharField(max_length=255, blank=False, null=False)
    slug = models.SlugField(max_length=255)
    short_description = models.TextField(null=False, blank=True)
    description = models.TextField(null=False, blank=False)
    logo = CustomImageField(upload_to=generate_upload_path, storage=image_storage,
                            sizes=['big', 'small', 'th'], max_length=255, blank=True)
    keywords = models.CharField(max_length=2048, blank=True, null=False)
    director = models.CharField(max_length=255, blank=True, null=False)
    address = models.CharField(max_length=2048, blank=True, null=False)
    slogan = models.CharField(max_length=2048, blank=True, null=False)
    company_paypal_account = models.EmailField(blank=True, null=True)
    metadata = HStoreField()
    branches = models.ManyToManyField(Branch)
    additional_pages = GenericRelation(AdditionalPage)
    galleries = GenericRelation(Gallery)
    documents = GenericRelation(Document)

    def upload_images(self):
        from core import tasks
        params = {
            'file': self.logo.path,
            'sizes': {
                'big': {'box': (500, 500), 'fit': False},
                'small': {'box': (200, 200), 'fit': False},
                'th': {'box': (80, 80), 'fit': True}
            }
        }

        tasks.upload_images.delay(params)

    def reindex(self, is_active_changed=False, **kwargs):
        from core import tasks
        reindex_instance(self)

        if is_active_changed:
            task_id = 'company:on_company_active_changed:%s' % self.pk
            app.control.revoke(task_id)
            tasks.on_company_active_changed.apply_async((self.pk,), tasks_id=task_id)

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
    def get_index_model(**kwargs):
        from b24online.search_indexes import CompanyIndex
        return CompanyIndex

    @property
    def gallery_images(self):
        model_type = ContentType.objects.get_for_model(self)
        return GalleryImage.objects.filter(gallery__content_type=model_type, gallery__object_id=self.pk)

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    slug = models.SlugField(max_length=255)
    organization = models.ForeignKey(Organization, db_index=True, related_name='departments')

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def has_perm(self, user):
        return self.organization.has_perm(user)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('department:detail', args=[self.slug, self.pk])

    def create_vacancy(self, name, user, **kwargs):
        return Vacancy.objects.create(
            name=name,
            created_by=user,
            updated_by=user,
            department=self,
        )


class Vacancy(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    slug = models.SlugField(max_length=255)
    department = models.ForeignKey(Department, related_name='vacancies', db_index=True, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='work_positions')
    is_hidden_user = models.BooleanField(_('Hide the vacancy user'), 
                                        default=False, db_index=True)
    staffgroup = models.ManyToManyField('StaffGroup', 
                                        related_name='group_vacancies')
    permission_extra_group = models.ManyToManyField('PermissionsExtraGroup', 
                                        related_name='extra_group_vacancies')

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_update_user')
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


class BusinessProposalCategory(MPTTModel, IndexedModelMixin):
    name = models.CharField(max_length=255, blank=False, null=False)
    slug = models.SlugField(max_length=255)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    @staticmethod
    def get_index_model(**kwargs):
        from b24online.search_indexes import BusinessProposalCategoryIndex
        return BusinessProposalCategoryIndex

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('bp_category:detail', args=[self.slug, self.pk])


class BusinessProposal(ActiveModelMixing, models.Model, IndexedModelMixin):
    class Meta:
        ordering = ["-id"]

    title = models.CharField(max_length=255, blank=False, null=False)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=False, null=False)
    keywords = models.CharField(max_length=2048, blank=True, null=False)
    additional_pages = GenericRelation(AdditionalPage)
    documents = GenericRelation(Document)
    branches = models.ManyToManyField(Branch)
    galleries = GenericRelation(Gallery)
    country = models.ForeignKey(Country)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    categories = models.ManyToManyField(BusinessProposalCategory)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='proposals')
    context_advertisements = GenericRelation(ContextAdvertisement)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def has_perm(self, user):
        return self.organization.has_perm(user)

    @staticmethod
    def get_index_model(**kwargs):
        from b24online.search_indexes import BusinessProposalIndex
        return BusinessProposalIndex

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('proposal:detail', args=[self.slug, self.pk])

    @property
    def gallery_images(self):
        model_type = ContentType.objects.get_for_model(self)
        return GalleryImage.objects.filter(gallery__content_type=model_type, gallery__object_id=self.pk)


class InnovationProject(ActiveModelMixing, models.Model, IndexedModelMixin):
    name = models.CharField(max_length=2048, blank=False, null=False)
    slug = models.SlugField(max_length=2048)
    description = models.TextField(blank=False, null=False)
    product_name = models.CharField(max_length=2048, blank=False, null=False)
    business_plan = models.TextField(blank=False, null=False)
    documents = GenericRelation(Document)
    currency = models.CharField(max_length=255, blank=False, null=True, choices=CURRENCY)
    cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=False)
    organization = models.ForeignKey(Organization, null=True, on_delete=models.CASCADE)
    branches = models.ManyToManyField(Branch)
    metadata = HStoreField()
    keywords = models.CharField(max_length=2048, blank=True, null=False)
    galleries = GenericRelation(Gallery)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    additional_pages = GenericRelation(AdditionalPage)
    context_advertisements = GenericRelation(ContextAdvertisement)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def has_perm(self, user):
        if not user.is_authenticated() or user.is_anonymous():
            return False

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
    def get_index_model(**kwargs):
        from b24online.search_indexes import InnovationProjectIndex
        return InnovationProjectIndex

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('innov:detail', args=[self.slug, self.pk])


class B2BProductCategory(MPTTModel, IndexedModelMixin):
    name = models.CharField(max_length=255, blank=False, null=False)
    slug = models.SlugField(max_length=255)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    image = CustomImageField(storage=image_storage, blank=True, null=True)

    @staticmethod
    def get_index_model(**kwargs):
        from b24online.search_indexes import B2bProductCategoryIndex
        return B2bProductCategoryIndex

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('b2b_category:detail', args=[self.slug, self.pk])


class B2BProduct(ActiveModelMixing, models.Model, IndexedModelMixin):
    name = models.CharField(max_length=2048, blank=False, name=False)
    slug = models.SlugField(max_length=2048)
    short_description = models.TextField(null=False)
    description = models.TextField(blank=False, null=False)
    image = CustomImageField(upload_to=generate_upload_path, storage=image_storage, sizes=['big', 'small', 'th'],
                             blank=True, null=True, max_length=255)
    categories = models.ManyToManyField(B2BProductCategory, related_name='products')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='b2b_products')
    keywords = models.CharField(max_length=2048, blank=True, null=False)
    currency = models.CharField(max_length=255, blank=True, null=True, choices=CURRENCY)
    measurement_unit = models.CharField(max_length=255, blank=True, null=True, choices=MEASUREMENT_UNITS)
    cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    producer = models.ForeignKey('Producer', related_name='b2b_products', 
                                 verbose_name=_('Producer'), 
                                 null=True, blank=True)
    documents = GenericRelation(Document)
    galleries = GenericRelation(Gallery)
    branches = models.ManyToManyField(Branch)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    additional_pages = GenericRelation(AdditionalPage)
    metadata = HStoreField()
    context_advertisements = GenericRelation(ContextAdvertisement)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

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

    def reindex(self, **kwargs):
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
    def get_index_model(**kwargs):
        from b24online.search_indexes import B2BProductIndex
        return B2BProductIndex

    def has_perm(self, user):
        return self.company.has_perm(user)

    def get_absolute_url(self):
        return reverse('products:detail', args=[self.slug, self.pk])

    class Meta:
        index_together = [
            ['created_at', 'company'],
        ]

    @property
    def gallery_images(self):
        model_type = ContentType.objects.get_for_model(self)
        return GalleryImage.objects.filter(gallery__content_type=model_type, gallery__object_id=self.pk)

    def get_contextmenu_options(self, context):
        """
        Return extra options for context menu.
        """
        
        # FIXME: (andrus) add the conditions for site
        model_type = ContentType.objects.get_for_model(self)
        if getattr(self, 'pk', False):
            yield (reverse('questionnaires:list_for_item',
                           kwargs={'content_type_id': model_type.id, 
                                   'item_id': self.id}),
                   _('Questionnaire'))
            

class B2BProductComment(MPTTModel):
    content = models.TextField()
    product = models.ForeignKey(B2BProduct, on_delete=models.CASCADE)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def has_perm(self, user):
        if not user.is_authenticated() or user.is_anonymous():
            return False

        return user.is_commando or user.is_superuser or self.created_by == user


class NewsCategory(MPTTModel, IndexedModelMixin):
    name = models.CharField(max_length=255, blank=False, null=False, db_index=True)
    image = CustomImageField(storage=image_storage, blank=True, null=True)
    slug = models.SlugField(max_length=255)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    @staticmethod
    def get_index_model(**kwargs):
        from b24online.search_indexes import NewsCategoryIndex
        return NewsCategoryIndex

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('news_category:detail', args=[self.slug, self.pk])


class Greeting(models.Model, IndexedModelMixin):
    photo = CustomImageField(upload_to=generate_upload_path, storage=image_storage, sizes=['big'],
                             max_length=255, blank=True)
    organization_name = models.CharField(max_length=255, blank=False, null=False)
    name = models.CharField(max_length=255, blank=False, null=False)
    slug = models.SlugField(max_length=255)
    position_name = models.CharField(max_length=255, blank=False, null=False)
    content = models.TextField(blank=False, null=False)

    @staticmethod
    def get_index_model(**kwargs):
        from b24online.search_indexes import GreetingIndex
        return GreetingIndex

    def __str__(self):
        return self.name

    def has_perm(self, user):
        if not user.is_authenticated() or user.is_anonymous():
            return False

        return user.is_superuser or user.is_commando

    def upload_images(self):
        from core import tasks
        params = {
            'file': self.photo.path,
            'sizes': {
                'big': {'box': (500, 500), 'fit': False},
            }
        }

        tasks.upload_images.delay(params)

    def reindex(self, **kwargs):
        reindex_instance(self)

    def get_absolute_url(self):
        return reverse('greetings:detail', args=[self.slug, self.pk])


class News(ActiveModelMixing, models.Model, IndexedModelMixin):
    class Meta:
        ordering = ["-id"]

    title = models.CharField(max_length=255, blank=False, null=False)
    image = CustomImageField(upload_to=generate_upload_path, storage=image_storage,
                             sizes=['big', 'small', 'th'], max_length=255, blank=True)
    slug = models.SlugField(max_length=255)
    short_description = models.TextField()
    content = models.TextField()
    is_tv = models.BooleanField(default=False)
    categories = models.ManyToManyField(NewsCategory)
    galleries = GenericRelation(Gallery)
    video_code = models.CharField(max_length=255, blank=True, null=True)
    keywords = models.CharField(max_length=2048, blank=True, null=False)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    organization = models.ForeignKey(Organization, null=True, on_delete=models.CASCADE, related_name='news')
    country = models.ForeignKey(Country, null=True)
    context_advertisements = GenericRelation(ContextAdvertisement)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def gallery_images(self):
        model_type = ContentType.objects.get_for_model(self)
        return GalleryImage.objects.filter(gallery__content_type=model_type, gallery__object_id=self.pk)

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

    @staticmethod
    def get_index_model(**kwargs):
        from b24online.search_indexes import NewsIndex
        return NewsIndex

    def __str__(self):
        return self.title

    def has_perm(self, user):
        if not user.is_authenticated() or user.is_anonymous():
            return False

        if self.organization:
            return self.organization.has_perm(user)

        return user.is_commando or user.is_superuser

    def get_absolute_url(self):
        if self.is_tv:
            return reverse('tv:detail', args=[self.slug, self.pk])

        return reverse('news:detail', args=[self.slug, self.pk])


class Tender(ActiveModelMixing, models.Model, IndexedModelMixin):
    title = models.CharField(max_length=2048, blank=False, null=False)
    slug = models.SlugField(max_length=2048)
    content = models.TextField(blank=False, null=False)
    currency = models.CharField(max_length=255, blank=False, null=True, choices=CURRENCY)
    cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=False)
    branches = models.ManyToManyField(Branch)
    documents = GenericRelation(Document)
    keywords = models.CharField(max_length=2048, blank=True, null=False)
    dates = DateRangeField(null=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    additional_pages = GenericRelation(AdditionalPage)
    country = models.ForeignKey(Country)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    galleries = GenericRelation(Gallery)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_update_user')
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
    def get_index_model(**kwargs):
        from b24online.search_indexes import TenderIndex
        return TenderIndex

    def has_perm(self, user):
        return self.organization.has_perm(user)

    def get_absolute_url(self):
        return reverse('tenders:detail', args=[self.slug, self.pk])


class Profile(ActiveModelMixing, models.Model, IndexedModelMixin):
    first_name = models.CharField(max_length=255, blank=False, null=True)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    avatar = CustomImageField(upload_to=generate_upload_path, storage=image_storage,
                              sizes=['big', 'small', 'th'], max_length=255, blank=True, null=True)
    mobile_number = models.CharField(max_length=255, blank=True, null=True)
    site = models.URLField(max_length=255, blank=True, null=True)
    profession = models.CharField(max_length=255, blank=True, null=True)
    country = models.ForeignKey(Country)
    birthday = models.DateField(null=True, blank=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="profile", on_delete=models.CASCADE)

    GENDERS = [('male', _('Male')), ('female', _('Female'))]
    sex = models.CharField(max_length=255, default='male', choices=GENDERS)

    TYPES = [('businessman', _('Businessman')), ('individual', _('Individual'))]
    user_type = models.CharField(max_length=255, default='individual', choices=TYPES)

    def upload_images(self):
        from core import tasks
        params = {
            'file': self.avatar.path,
            'sizes': {
                'big': {'box': (150, 150), 'fit': False},
                'small': {'box': (100, 100), 'fit': False},
                'th': {'box': (30, 30), 'fit': True}
            }
        }

        tasks.upload_images.delay(params)

    def reindex(self, **kwargs):
        reindex_instance(self)

    @property
    def full_name(self):
        return ' ' . join(
            filter(None, [self.first_name, self.middle_name, self.last_name])
        )

    @staticmethod
    def get_index_model(**kwargs):
        from b24online.search_indexes import ProfileIndex
        return ProfileIndex

    def __str__(self):
        return self.full_name

    def has_perm(self, user):
        if not user.is_authenticated() or user.is_anonymous():
            return False

        return user.is_commando or user.is_superuser or self.user == user


class Exhibition(ActiveModelMixing, models.Model, IndexedModelMixin):
    title = models.CharField(max_length=255, blank=False, null=False)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=False, null=False)
    documents = GenericRelation(Document)
    keywords = models.CharField(max_length=2048, blank=True, null=False)
    dates = DateRangeField(null=True)
    city = models.CharField(max_length=255, blank=False, null=True)
    route = models.CharField(blank=True, null=False, max_length=2048)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    country = models.ForeignKey(Country)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    additional_pages = GenericRelation(AdditionalPage)
    context_advertisements = GenericRelation(ContextAdvertisement)
    branches = models.ManyToManyField(Branch)
    metadata = HStoreField()
    galleries = GenericRelation(Gallery)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_update_user')
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

    def reindex(self, **kwargs):
        reindex_instance(self)

    @staticmethod
    def get_index_model(**kwargs):
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
    slug = models.SlugField(max_length=255)
    content = models.TextField(blank=False, null=False)
    is_on_top = models.BooleanField(default=False)

    SITE_TYPES = [
        ('b2b', _('B2B')),
        ('b2c', _('B2C')),
        ('user_site', _('User sites'))
    ]

    site_type = models.CharField(max_length=10, choices=SITE_TYPES, default='b2b')

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
        if not user.is_authenticated() or user.is_anonymous():
            return False

        return user.is_commando or user.is_superuser

    def get_absolute_url(self):
        return reverse('project:detail', args=[self.slug, self.pk])

    class Meta:
        index_together = [
            ['page_type', 'site_type'],
        ]


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="notifications")
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


class MessageChat(AbstractRegisterInfoModel):
    """
    Class for messages chat.
    """
    OPENED, CLOSED = 'opened', 'closed'
    STATUSES = (
        (OPENED, _('Opened')),
        (CLOSED, _('Closed')),
    )
    subject = models.CharField(_('Chat subject'), max_length=255,
                               null=True, blank=False) 
    organization = models.ForeignKey('Organization', related_name='chats', 
                                     null=True, blank=True)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, 
                                  related_name='incoming_chats', null=True,
                                  blank=True)
    participants = models.ManyToManyField(User, blank=True)    
    is_private = models.NullBooleanField()
    status = models.CharField(_('Chart status'), max_length=10, 
                              choices=STATUSES, default=OPENED, editable=False,
                              null=False, db_index=True)

    class Meta:
        verbose_name = _('Messages chat')    
        verbose_name_plural = _('Messages chats')    

    def is_incoming(self, user):
        return self.created_at.pk == user.pk
        
    def get_participants(self):
        return self.participants.all()


class Message(models.Model):
    """
    Class for inner messages.
    """
    DRAFT, READY, READ = 'draft', 'ready', 'read'
    STATUSES = (
        (DRAFT, _('Draft')),
        (READY, _('Ready')),
        (READ, _('Read')),
    )

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, 
                               related_name='outgoing_messages')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, 
                                  related_name='incoming_messages', null=True,
                                  blank=True)
    organization = models.ForeignKey('Organization', 
                                     related_name='organization_messages', 
                                     null=True, blank=True)
    chat = models.ForeignKey(MessageChat, related_name='chat_messages',
                             null=True, blank=True)
    is_read = models.BooleanField(default=False)
    subject = models.CharField(_('Chat subject'), max_length=255,
                               null=True, blank=True, db_index=True) 
    content = models.TextField(blank=False, null=False)
    status = models.CharField(_('Message status'), max_length=10, 
                              choices=STATUSES, default=DRAFT, editable=False,
                              null=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        index_together = [
            ['recipient', 'sender'],
        ]

    @classmethod
    def add_message(cls, content, sender, recipient_id, notify=True):
        with transaction.atomic():
            recipient = get_user_model().objects.get(pk=recipient_id)
            cls.objects.create(sender=sender, content=content, recipient=recipient)

        if notify:
            from appl import func
            func.publish_realtime('private_massage', recipient=recipient_id, fromUser=sender.pk)

    def __str__(self):
        return "From %s to %s at %s" % (self.sender.profile, self.recipient.profile, self.sent_at)

    def upload_files(self):
        from core import tasks

        images = []
        files = []
        for attachment in self.attachments.all():
            if attachment.is_image():
                images.append({
                    'file': os.path.join(
                        abspathu(settings.MEDIA_ROOT), 
                                 str(attachment.file)),
                    'sizes': {
                        'th': {'box': (50, 50), 'fit': False},
                    },
                })
            else:
                files.append({
                    'file': os.path.join(settings.MEDIA_ROOT, 
                                         str(attachment.file)),
                    'bucket_path': str(attachment.file),
                })
        if images:
            tasks.upload_images(*images)
        if files:
            tasks.upload_file(*files)


class MessageAttachment(models.Model):

    ICONS = {
        'application/vnd.ms-excel': 'xls.png',
        'application/msword': 'doc.png',
        'application/pdf': 'pdf.png',
    }

    message = models.ForeignKey('Message', related_name='attachments')
    file = models.FileField()
    file_name = models.CharField(_('File name'), max_length=255, null=True,
                                 blank=True, editable=False)
    content_type = models.CharField(_('Content type'), max_length=255, 
                                    null=True, blank=True, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, 
                                   related_name='%(class)s_create_user')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'Message attachment'
        verbose_name_plural = 'Messages attachments'

    def is_image(self):
        try:
            return self.content_type.split('/')[0] == 'image'
        except IndexError:
            return False

    def get_shorted_name(self, size=7):
        try:
            _file, _ext = self.file_name.split('.')
            if len(_file) > size:
                return '%s.%s' % (_file[:size], _ext)
            else:
                return self.file_name
        except ValueError:
            return self.file_name

    def get_icon(self):
        return 'b24online/img/' + \
            type(self).ICONS.get(self.content_type, 'unknown.png')


class BannerBlock(models.Model):
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    width = models.PositiveSmallIntegerField(null=True, blank=True)
    height = models.PositiveSmallIntegerField(null=True, blank=True)
    image = CustomImageField(storage=image_storage, null=True, blank=True)
    description = models.CharField(max_length=1024, null=True, blank=True)
    factor = models.FloatField(default=1)

    BLOCK_TYPES = [
        ('b2b', _('B2B')),
        ('b2c', _('B2C')),
        ('user_site', _('User sites'))
    ]

    block_type = models.CharField(max_length=10, choices=BLOCK_TYPES)

    def get_absolute_url(self):
        return reverse('adv_banners:banner_form', args=[self.pk])

    def __str__(self):
        return self.name

    class Meta:
        index_together = [
            ['code', 'block_type'],
        ]


class Banner(ActiveModelMixing, Advertisement):
    title = models.CharField(max_length=255)
    link = models.URLField()
    image = CustomImageField(upload_to=generate_upload_path, storage=image_storage, max_length=255, sizes=['big'])
    block = models.ForeignKey(BannerBlock, related_name='banners')
    organization = models.ForeignKey(Organization, null=True, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    site = models.ForeignKey(Site, null=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def upload_images(self):
        from core import tasks
        params = {
            'file': self.image.path,
        }

        tasks.upload_images.delay(params)


class AdvertisementOrder(Order):
    advertisement = models.OneToOneField(Advertisement)
    total_cost = models.DecimalField(max_digits=15, decimal_places=2, null=False, blank=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    purchaser = GenericForeignKey('content_type', 'object_id')
    price_components = models.ManyToManyField(AdvertisementPrice)
    paid = models.BooleanField(default=False)
    price_factor = models.FloatField(default=1)
    dates = DateRangeField()

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(default=timezone.now)
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
    def days(self):
        return (self.dates.upper - self.dates.lower).days

    def has_perm(self, user):
        if user is None or not user.is_authenticated() or user.is_anonymous():
            return False

        if user.is_superuser or user.is_commando:
            return True

        return self.purchaser.has_perm()


### Models for stats

class RegisteredEventType(models.Model):
    """
    The registered events types.
    """
    name = models.CharField(_('Name'), max_length=255, blank=False, null=False)
    slug = models.SlugField(_('Code'), max_length=20)

    class Meta:
        verbose_name = _('Registered events type')
        verbose_name_plural = _('Registered events types')

    def __unicode__(self):
        return self.name


##
# Models for stats
##
class RegisteredEventMixin(models.Model):
    """
    The registered events abstract class.
    """
    event_type = models.ForeignKey(RegisteredEventType,
                                   verbose_name=_('Event  type'))
    site = models.ForeignKey(Site, verbose_name=_('Site'),
                             null=True, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(_('Instance ID'))
    item = GenericForeignKey('content_type', 'object_id')

    class Meta:
        abstract = True


class RegisteredEventStats(RegisteredEventMixin):
    """
    The registered events stats per day.
    """
    registered_at = models.DateField(auto_now_add=True, db_index=True)
    unique_amount = models.PositiveIntegerField(_('Unique'))
    total_amount = models.PositiveIntegerField(_('Total'))
    extra_data = HStoreField(_('Event extra data'), blank=True, null=True)

    class Meta:
        verbose_name = _('Registered events stats')
        unique_together = ('event_type', 'site', 'content_type',
                           'object_id', 'registered_at')

    def __str__(self):
        return _('Event stats of type "{0}" for "{1}"'). \
            format(self.event_type.name, str(self.item))

    def get_kwargs(self):
        return {
            'event_type_id': self.event_type_id,
            'content_type_id': self.content_type_id,
            'instance_id': self.object_id,
        }

    def store_info(self, registered_event):
        """
        Increment the counters and store the GeoIP info.
        """
        cls = type(self)
        _add = {'unique': 1 if registered_event.is_unique else 0,
                'total': 1}
        data = registered_event.event_data
        if not self.extra_data or not isinstance(self.extra_data, dict):
            self.extra_data = {}
        if data:
            key_data = []
            for _key in ('country_code', 'country_name', 'city'):
                _value = data.get(_key)
                if not _value or _value == 'None':
                    _value = 'undef'
                key_data.append(_value.strip())
            for _type in ('unique', 'total'):
                _key = ':'.join(key_data + [_type, ])
                if _key in self.extra_data:
                    try:
                        _old = int(self.extra_data)
                    except TypeError:
                        _old = 0
                    _new = _old + _add.get(_type, 0)
                else:
                    _new = _add.get(_type, 0)
                self.extra_data[_key] = str(_new)
        self.unique_amount += _add['unique']
        self.total_amount += _add['total']
        self.save()

    def get_extra_info(self, cnt_type):
        """
        Return GeoIP info.
        """

        extra_info = []
        if not self.extra_data:
            if cnt_type == 'unique':
                cnt = self.unique_amount or 0
            else:
                cnt = self.total_amount or 0
            extra_info.append([ugettext('Undefined'), cnt,
                               [(ugettext('Undefined'), self.unique_amount or 0,
                                 self.total_amount or 0), ]])
        else:
            data = {}
            for item_key, item_value in self.extra_data.items():
                item_key_list = item_key.split(':')
                country_name, city, a_cnt_type = item_key_list[1:]
                try:
                    _value = int(item_value)
                except TypeError:
                    continue
                else:
                    data.setdefault(country_name, {}) \
                        .setdefault(city, {})[a_cnt_type] = _value
            extra_info = []
            for country_name, data_1 in data.items():
                cities = []
                country_amount = 0
                for city, data_2 in data_1.items():
                    cnt = data_2.get(cnt_type, 0)
                    country_amount += cnt
                    if not city or city == 'undef':
                        city = ugettext('Undefined')
                    add_2 = [city, cnt]
                    cities.append(add_2)
                add_1 = [country_name, country_amount, cities]
                extra_info.append(add_1)
        return extra_info


class RegisteredEvent(RegisteredEventMixin):
    """
    The registered events.

    Maybe could be replaced by Redis records.
    """

    registered_at = models.DateTimeField(auto_now_add=True,
                                         db_index=True)
    url = models.TextField(_('Requested URL'), blank=True, null=True)
    username = models.CharField(_('Username'), max_length=255,
                                blank=True, null=True)
    ip_address = models.GenericIPAddressField(_('IP address'),
                                              blank=True, null=True)
    user_agent = models.CharField(_('User Agent'), max_length=255,
                                  blank=True, null=True)
    event_hash = models.CharField(_('Event hash key'), max_length=32,
                                  validators=[MinLengthValidator(32)],
                                  null=False, default='', db_index=True)
    is_unique = models.BooleanField(_('Is unique'),
                                    default=False)
    event_data = HStoreField(_('Event extra data'), blank=True, null=True)

    class Meta:
        verbose_name = _('Registered event')
        verbose_name_plural = _('Registered events')
        unique_together = ('event_type', 'site', 'content_type',
                           'object_id', 'registered_at', 'ip_address',
                           'user_agent')

    def __str__(self):
        return _('Event of type "{0}" for "{1}"'). \
            format(self.event_type.name, str(self.item))

    @property
    def unique_key(self):
        """
        Return the unique key based on IP and UA.
        """
        meaning_data = (self.event_type.slug, self.ip_address,
                        self.user_agent, self.content_type.id,
                        self.object_id)
        key_str_raw = ':'.join(map(smart_str, meaning_data))
        key_str = key_str_raw.encode('utf-8')
        return hashlib.md5(key_str).hexdigest()

    def check_is_unique(self):
        # FIXME: replace by Redis
        cls = type(self)
        try:
            cls.objects.filter(event_type=self.event_type,
                               site=self.site, content_type=self.content_type,
                               object_id=self.object_id, event_hash=self.unique_key,
                               registered_at__startswith=datetime.date.today())[0]
        except IndexError:
            return True
        else:
            return False

    @property
    def geo_info(self):
        if not self.event_data:
            return None
        data = []
        for item_code, item_name in (
                ('country_code', _('Country code')),
                ('country_name', _('Country name')),
                ('city', _('City'))):
            item_value = self.event_data.get(item_code)
            if item_value:
                data.append('{0} : {1}'.format(item_name, item_value))
        if data:
            return ', '.join(data)
        else:
            return None


class DealOrder(ActiveModelMixing, AbstractRegisterInfoModel):
    """
    The model class for Client Orders to buy Products.

    Assume that the order creator is a customer person or a delegate of
    customer company.
    """
    AS_ORGANIZATION, AS_PERSON = 'organization', 'person'
    CUSTOMER_TYPES = ((AS_PERSON, _('Person')),
                      (AS_ORGANIZATION, _('Organization')),)

    DRAFT, READY, PARTIALLY, PAID = 'draft', 'ready', 'partially', 'paid'
    STATUSES = ((DRAFT, _('Draft')), (READY, _('Ready')),
                (PARTIALLY, _('Partially paid')), (PAID, _('Paid')))

    customer_type = models.CharField(_('Customer type'), max_length=15,
                                     choices=CUSTOMER_TYPES,
                                     null=False, blank=False)
    customer_organization = models.ForeignKey(
        'Organization',
        related_name='deal_orders',
        verbose_name=_('Customer organization'),
        null=True, blank=True)
    order_no = models.CharField(_('Order No.'), max_length=50,
                                blank=True, null=True, db_index=True)
    paid_at = models.DateTimeField(_('Payment datetime'), editable=False,
                                   null=True, blank=True, db_index=True)
    status = models.CharField(_('Order status'), max_length=10,
                              choices=STATUSES, default=DRAFT, editable=False,
                              null=False, blank=False)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = _('Product order')
        verbose_name_plural = _('Product orders')

    @classmethod
    def get_user_orders(cls, user, status=DRAFT):
        """
        Return the qs for DealOrders where the user is a customer.
        """
        if user.is_authenticated():
            org_ids = get_objects_for_user(
                user, ['b24online.manage_organization'],
                Organization.get_active_objects().all(), with_superuser=False)
            return cls.objects.filter(status=status).filter(
                (Q(customer_type=cls.AS_PERSON) & Q(created_by=user)) | \
                (Q(customer_type=cls.AS_ORGANIZATION) & \
                    Q(customer_organization__in=org_ids)))
        else:
            return cls.objects.none()

    def __str__(self):
        _data = [_('Order from %s') % self.created,]
        if self.order_no:
            _data.append('%s %s' % (_('order No.') % self.order_no))
        return ', ' . join(_data)

    def can_pay(self):
        return self.status == self.DRAFT

    @property
    def customer_person(self):
        return self.created_by 
        
    def get_customer_type(self):
        """
        Return the customer type title: Company or Person.
        """
        return type(self).CUSTOMER_TYPES.get(self.customer_type)

    def get_customer(self):
        if self.customer_type == self.AS_PERSON:
            if self.created_by.profile:
                return self.created_by.profile.full_name or self.created_by.email
            else:
                return self.created_by
        elif self.customer_type == self.AS_ORGANIZATION:
            return self.customer_organization
        else:
            return None

    def get_deals(self):
        """
        Return all Order's deals.
        """
        return self.order_deals.order_by('id')

    def get_draft_deals(self):
        """
        Return all Order's deals.
        """
        return self.order_deals.filter(status='draft').order_by('id')

    def get_status(self):
        """
        Return the order status.
        """
        return dict(type(self).STATUSES).get(self.status)

    #def get_total_cost(self):
    #    """
    #    Return deal cost in different currencies.
    #    """
    #    qs = self.order_deals.annotate(cost=Sum('total_cost')).values()
    #    for currency, cost in self.total_cost_data.items():
    #        yield (cost, currency)

    @transaction.atomic
    def pay(self):
        """
        Pay the order.
        """
        cls = type(self)
        for deal in Deal.objects.filter(Q(deal_order=self) & ~Q(status=Deal.PAID)):
            deal.status = Deal.PAID
            deal.save()
        self.status = cls.PAID
        self.save()


class Deal(ActiveModelMixing, AbstractRegisterInfoModel):
    """    The model class for Orders Deal to buy Products.

    The deal No. has been added as some organization can keep records about every
    deal.
    """
    DRAFT, READY, PAID, ORDERED, REJECTED = \
        'draft', 'ready', 'paid', 'ordered', 'rejected'
    STATUSES = ((DRAFT, _('Draft')), (READY, _('Ready')),
                (PAID, _('Paid')), (ORDERED, _('Ordered by Email')),
                (REJECTED, _('Rejected')))

    deal_order = models.ForeignKey(DealOrder, related_name='order_deals',
                              verbose_name=_('Order'), null=False, blank=False,
                              editable=False)
    supplier_company = models.ForeignKey('Company',
                                         related_name='company_deals',
                                         verbose_name=_('Supplier company'),
                                         null=False, blank=False,
                                         editable=False)
    deal_no = models.CharField(_('Deal No.'), max_length=50,
                                blank=True, null=True, db_index=True)
    total_cost = models.DecimalField(_('Total deal cost'),
                                     max_digits=15, decimal_places=2, 
                                     null=True, blank=False, editable=False)
    currency = models.CharField(_('Currence'), max_length=255, blank=True,
                                null=True, choices=CURRENCY)
    paid_at = models.DateTimeField(_('Payment datetime'), editable=False,
                                   null=True, blank=True, db_index=True)
    status = models.CharField(_('Deal status'), max_length=10,
                              choices=STATUSES, default=DRAFT, editable=False,
                              null=False, blank=False)
    person_first_name = models.CharField(_('First name'), max_length=255,
                                            blank=True, null=True)
    person_last_name = models.CharField(_('Last name'), max_length=255,
                                 blank=True, null=True)
    person_phone_number = models.CharField(_('Phone number'), max_length=255,
                                    blank=True, null=True)
    person_country = models.ForeignKey(Country, verbose_name=_('Country'),
                                       blank=True, null=True)
    person_address = models.CharField(_('Address'), max_length=2048,
                                      blank=True, null=False)
    person_email = models.EmailField(verbose_name='E-mail',
                                     blank=True, null=True,
                                     max_length=255, db_index=True)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Purchase deal')
        verbose_name_plural = _('Purchase deal')

    @classmethod
    def get_current_deals(cls, request, statuses=None):
        """
        Return the deals for user's companies.
        """
        current_organization = get_current_organization(request)
        if request.user.is_authenticated() and \
            isinstance(current_organization, Company):
            qs = cls.objects.filter(
                supplier_company=current_organization,
            )
            if statuses:
                qs = qs.filter(status__in=statuses)
        else:
            qs = cls.objects.none()
        return qs

    @classmethod
    def get_qs_cost(cls, qs):
        """
        Return the total cost for qs as dictionary like `{currency: 123.00}`
        """
        totals = {}
        if qs.model == cls:
            for deal in qs:
                if deal.total_cost and deal.currency:
                    if deal.currency not in totals:
                        totals[deal.currency] = deal.total_cost
                    else:
                        totals[deal.currency] += deal.total_cost
        return totals

    def __str__(self):
        _data = [_('Deal from %s') % self.created,]
        if self.deal_no:
            _data.append(_('deal No. %s') % self.deal_no)
        return ', ' . join(_data)

    @property
    def description(self):
        _data = [_('Deal from %s for order %s') % (self.created, self.deal_order)]
        if self.deal_no:
            _data.append(_('deal No. %s') % self.deal_no)
        return ', ' . join(_data)

    def get_status(self):
        """
        Return the order status.
        """
        return dict(type(self).STATUSES).get(self.status)

    def get_items(self):
        """
        Return the qs for deal items.
        """
        return DealItem.objects.filter(deal=self).order_by('id')

    def can_pay(self):
        return self.status == self.DRAFT

    def can_edit(self):
        return self.status in (self.READY, self.DRAFT)

    def pay(self):
        """
        Pay the deal.
        """
        self.status = self.ORDERED
        self.save()


class DealItem(models.Model):
    """
    The model class for Deal Item.

    ContentType is limited only by B2BProduct and B2CProduct.
    Add the cost (price) because need to remember the price on deal datetime.
    """
    CONTENT_TYPE_LIMIT = models.Q(app_label='b24online', model='b2bproduct') | \
        models.Q(app_label='centerpokupok', model='b2cproduct')

    deal = models.ForeignKey(Deal, related_name='deal_products',
                              verbose_name=_('Deal'), null=False, blank=False,
                              editable=False)
    content_type = models.ForeignKey(ContentType,
                                     limit_choices_to=CONTENT_TYPE_LIMIT,
                                     on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    cost = models.DecimalField(_('The product price'),
                               max_digits=15, decimal_places=2,
                               null=True, blank=True)
    currency = models.CharField(_('Currence'), max_length=255, blank=True,
                                null=True, choices=CURRENCY)
    quantity = models.PositiveIntegerField(_('Quantity'))

    class Meta:
        verbose_name = 'Deal product'
        verbose_name_plural = 'Deal products'

    def get_total(self):
        """
        Return the total cost
        """
        return self.cost * self.quantity if self.cost and self.quantity \
            else 0


class StaffGroup(models.Model):
    """
    Class for the relations of :class:`auth.models.Group` for 
    organization's staff vacancies.
    """
    group = models.OneToOneField(Group, verbose_name=_('Vacancy group'))

    class Meta:
        verbose_name = 'Group for staff'
        verbose_name_plural = 'Groups for staff'

    @classmethod
    def get_options(cls):
        return ((item.id, item.group.name) \
            for item in cls.objects.select_related('group')\
                .order_by('group__name'))


class PermissionsExtraGroup(models.Model):
    """
    Class for permission's addiotional groups.
    """
    name = models.CharField(_('Group name'), max_length=255, 
                            blank=False, null=False)
    permissions = models.ManyToManyField(
        Permission, 
        verbose_name=_('Permission extra group')
    )

    class Meta:
        verbose_name = _('Permission\'s extra group')
        verbose_name_plural = _('Permission\'s extra groups')

    @classmethod
    def get_options(cls):
        return ((item.id, item.name) \
            for item in cls.objects.order_by('name'))


class Producer(models.Model):
    """
    The model class for goods producers.
    """
    name = models.CharField(_('Name'), max_length=255, 
                            blank=False, null=False)
    slug = models.SlugField(max_length=255)
    short_description = models.TextField(_('Short description'), 
                                         null=True, blank=True)
    description = models.TextField(_('Descripion'), null=True, blank=True)
    logo = CustomImageField(upload_to=generate_upload_path, 
                            storage=image_storage,
                            sizes=['big', 'small', 'th'],
                            max_length=255, null=True, blank=True)
    country = models.CharField(_('Country'), max_length=255, 
                               null=True, blank=True)
                               
    class Meta:
        verbose_name = _('Products producer')
        verbose_name_plural = _('Products producers')

    def __str__(self):
        return self.name

    def upload_logo(self, changed_data=None):
        from core import tasks
        params = []
        if (changed_data is None or 'logo' in changed_data) and self.logo:
            params.append({
                'file': self.logo.path,
                'sizes': {
                    'small': {'box': (24, 24), 'fit': False},
                    'th': {'box': (50, 50), 'fit': False}
                }
            })
        tasks.upload_images(*params, async=False)

##
# Models for Questionnaires
##
class Questionnaire(ActiveModelMixing, AbstractRegisterInfoModel):
    """
    The main model class for Questionnaire sub-app.
    """
    # The content types are limited by set (B2BProduct, B2CProduct)
    CONTENT_TYPE_LIMIT = models.Q(app_label='b24online', model='b2bproduct') |\
        models.Q(app_label='centerpokupok', model='b2cproduct')

    name = models.CharField(_('Questionnaire title'), max_length=255, 
                            blank=False, null=False)
    short_description = models.TextField(_('Short description'), 
                                         null=True, blank=True)
    description = models.TextField(_('Descripion'), null=True, blank=True)
    image = CustomImageField(upload_to=generate_upload_path, 
                             storage=image_storage,
                             sizes=['big', 'small', 'th'],
                             max_length=255, null=True, blank=True)
    content_type = models.ForeignKey(ContentType,
                                     limit_choices_to=CONTENT_TYPE_LIMIT,
                                     on_delete=models.CASCADE,
                                     null=False, blank=False)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    participants = models.ManyToManyField(User, blank=True)    
        
    class Meta:
        verbose_name = _('Questionnaire')
        verbose_name_plural = _('Questionnaires')

    def __str__(self):
        return self.name

    def upload_image(self, changed_data=None):
        from core import tasks
        params = []
        if (changed_data is None or 'image' in changed_data) and self.image:
            params.append({
                'file': self.image.path,
                'sizes': {
                    'small': {'box': (24, 24), 'fit': False},
                    'th': {'box': (50, 50), 'fit': False}
                }
            })
        tasks.upload_images(*params, async=False)


class Question(ActiveModelMixing, AbstractRegisterInfoModel):
    """
    The 'Question' models class.    
    """
    # Who created the question
    BY_AUTHOR, BY_MEMBER = 'author', 'member'
    WHO_CREATED = (
        (BY_AUTHOR, _('By author')),
        (BY_MEMBER, _('By member')),
    )
    
    questionnaire = models.ForeignKey(
        Questionnaire, 
        related_name='questions',
    )
    who_created = models.CharField(
        _('Who is the author'), 
        max_length=10,
        choices=WHO_CREATED, 
        default=BY_AUTHOR, 
        null=True, 
        blank=True
    )
    question_text = models.TextField(
        _('Question text'), 
        blank=False, 
        null=False
    )
    description = models.TextField(
        _('Descripion'), 
        null=True, 
        blank=True
    )
    score_positive = models.IntegerField(
        _('The question positive answer score'),
        null=True,
        blank=True,
    )
    score_negative = models.IntegerField(
        _('The question negative answer score'),
        null=True,
        blank=True,
    )
    position = models.PositiveIntegerField(
        _('The question position in the set'),
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')
        
    def __str__(self):
        return self.question_text
        

class Recommendation(ActiveModelMixing, AbstractRegisterInfoModel):
    """
    The 'Recommendation' models class.    
    """
    name = models.CharField(
        _('Name'), 
        max_length=255, 
        blank=False, 
        null=False
    )
    questionnaire = models.ForeignKey(
        Questionnaire, 
        related_name='recommendations',
    )
    description = models.TextField(
        _('Descripion'), 
        null=True, 
        blank=True
    )
    coincidences = models.IntegerField(
        _('How many coincidences'),
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Recommendation')
        verbose_name_plural = _('Recommendations')
        
    def __str__(self):
        return self.question_text
        

class Answer(ActiveModelMixing, AbstractRegisterInfoModel):
    """
    The 'Question answer' models class.    
    """
    ANSWER_YES, ANSWER_NO, ANSWER_OWN = 'author', 'member', 'own'
    ANSWER_TYPES = (
        (ANSWER_YES, _('Yes')),
        (ANSWER_NO, _('No')),
        (ANSWER_OWN, _('Own answer text'))
    )
    question = models.ForeignKey(
        Question, 
        related_name='questions',
        verbose_name=_('Question'),
    )
    participant = models.ForeignKey(
        User, 
        related_name='answers',
        verbose_name=_('Answer author'),
    )
    answer_type = models.CharField(
        _('Answer type'), 
        max_length=10,
        choices=ANSWER_TYPES, 
        default=ANSWER_YES, 
        null=True, 
        blank=True
    )
    answer_text = models.TextField(
        _('Question text'), 
        blank=False, 
        null=False
    )
    
    class Meta:
        verbose_name = _('Question answer')
        verbose_name_plural = _('Questions answers')

    def __str__(self):
        return self.answer_text
        

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

        instance.slug = uuslug(string, instance=instance)  # create_slug(string)


@receiver(post_save, sender=Company)
@receiver(post_save, sender=Chamber)
def initial_department(sender, instance, created, **kwargs):
    if not instance.created_by.is_superuser and not instance.created_by.is_commando and created:
        department = instance.create_department('Administration', instance.created_by)
        vacancy = instance.create_vacancy('Admin', department, instance.created_by)
        vacancy.assign_employee(instance.created_by, True)


@receiver(post_save, sender=Country)
@receiver(post_save, sender=Branch)
@receiver(post_save, sender=B2BProductCategory)
@receiver(post_save, sender=BusinessProposalCategory)
@receiver(post_save, sender=NewsCategory)
def index_item(sender, instance, created, **kwargs):
    instance.reindex()


@receiver(user_registered)
def initial_profile(sender, user, request, **kwargs):
    Profile.objects.create(user=user, country=Country.objects.first())


@receiver(post_save, sender=RegisteredEvent)
def process_event(sender, instance, created, **kwargs):
    """
    Process the registered event.
    """
    if instance.event_hash:
        # Try to get or create stats instance
        try:
            stats = RegisteredEventStats.objects \
                .get(event_type=instance.event_type,
                     site=instance.site,
                     content_type=instance.content_type,
                     object_id=instance.object_id,
                     registered_at=instance.registered_at.date())
        except RegisteredEventStats.DoesNotExist:
            stats = RegisteredEventStats(
                event_type=instance.event_type,
                site=instance.site,
                content_type=instance.content_type,
                object_id=instance.object_id,
                registered_at=instance.registered_at.date(),
                unique_amount=0, total_amount=0)

        # Increase the counters and store GeoIP info
        stats.store_info(instance)


@receiver(post_save, sender=Message)
def update_message_chat(sender, instance, created, **kwargs):
    """
    Recalculate product's deal cost after update.
    """
    assert isinstance(instance, Message), \
        _('Invalid parameter')

    if created and instance.chat:
        instance.chat.updated_by = instance.sender
        instance.chat.updated_at = instance.created_at
        instance.chat.save()


def recalculate_deal_cost(deal):
    """
    Recalculate total cost of deal
    """
    assert isinstance(deal, Deal), _('Invalid parameter')
    deal.total_cost = deal.deal_products\
        .aggregate(total_cost=Sum(F('cost') * F('quantity'),
            output_field=models.FloatField())).get('total_cost', 0.0)
    deal.save()


@receiver(post_save, sender=DealItem)
def recalculate_for_update(sender, instance, *args, **kwargs):
    """
    Recalculate product's deal cost after update.
    """
    recalculate_deal_cost(instance.deal)


@receiver(post_delete, sender=DealItem)
def recalculate_for_delete(sender, instance, *args, **kwargs):
    """
    Recalculate product's deal cost after delete.
    """
    if instance.deal.deal_products.exists():
        recalculate_deal_cost(instance.deal)
    elif instance.deal.status in (Deal.DRAFT, Deal.READY):
        instance.deal.delete()


@receiver(post_save, sender=Producer)
def upload_producer_logo(sender, instance, created, **kwargs):
    """
    Recalculate product's deal cost after update.
    """
    assert isinstance(instance, Producer), \
        _('Invalid parameter')

    instance.upload_logo()
