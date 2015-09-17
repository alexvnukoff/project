from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from b24online.models import Vacancy, Country, ContextAdvertisement
from b24online.utils import reindex_instance


class Requirement(models.Model):
    title = models.CharField(max_length=255, blank=False, null=False)
    slug = models.SlugField()
    vacancy = models.ForeignKey(Vacancy, related_name='job_requirement')
    city = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(blank=False, null=False)
    requirements = models.TextField(blank=False, null=False)
    terms = models.TextField(blank=False, null=False)
    is_anonymous = models.BooleanField(default=False)
    keywords = models.CharField(max_length=255, blank=True, null=False)
    country = models.ForeignKey(Country)
    context_advertisements = GenericRelation(ContextAdvertisement)

    TYPES_OF_EMPLOYMENT = [
        ('full_time', _('Full-time')),
        ('partial', _('Partial')),
        ('shifts', _('Shifts')),
        ('for_students', _('For students')),
    ]

    type_of_employment = models.CharField(max_length=10, null=False, blank=False, choices=TYPES_OF_EMPLOYMENT)
    is_active = models.BooleanField(default=True, db_index=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def reindex(self):
        reindex_instance(self)

    @property
    def organization(self):
        return self.vacancy.department.organization

    @staticmethod
    def get_index_model():
        from b24online.search_indexes import RequirementIndex
        return RequirementIndex

    def get_absolute_url(self):
        return reverse('vacancy:detail', args=[self.slug, self.pk])

    def has_perm(self, user):
        return self.vacancy.has_perm(user)

    def __str__(self):
        return self.title


class Resume(models.Model):
    MARTIAL_STATUSES = [
        ('married', _('Married')),
        ('widowed', _('Widowed')),
        ('separated', _('Separated')),
        ('divorced', _('Divorced')),
        ('single', _('Single')),
    ]

    STUDY_FORMS = [
        ('extramural', _('Extramural')),
        ('full_time', _('Full-time'))
    ]

    title = models.CharField(max_length=255, blank=False, null=False)
    slug = models.SlugField()
    martial_status = models.CharField(max_length=10, blank=True, null=True, choices=MARTIAL_STATUSES)
    nationality = models.CharField(max_length=255, null=False, blank=True)
    telephone_number = models.CharField(max_length=255)
    address = models.CharField(max_length=255, null=True, blank=True)
    faculty = models.CharField(max_length=255, null=True, blank=True)
    profession = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    is_active = models.BooleanField(default=True, db_index=True)
    study_start_date = models.DateField(blank=True, null=True)
    study_end_date = models.DateField(blank=True, null=True)
    study_form = models.CharField(max_length=30, choices=STUDY_FORMS, null=True, blank=True)
    company_exp_1 = models.CharField(max_length=255, null=True, blank=True)
    company_exp_2 = models.CharField(max_length=255, null=True, blank=True)
    company_exp_3 = models.CharField(max_length=255, null=True, blank=True)
    position_exp_1 = models.CharField(max_length=255, null=True, blank=True)
    position_exp_2 = models.CharField(max_length=255, null=True, blank=True)
    position_exp_3 = models.CharField(max_length=255, null=True, blank=True)
    start_date_exp_1 = models.DateField(blank=True, null=True)
    start_date_exp_2 = models.DateField(blank=True, null=True)
    start_date_exp_3 = models.DateField(blank=True, null=True)
    end_date_exp_1 = models.DateField(blank=True, null=True)
    end_date_exp_2 = models.DateField(blank=True, null=True)
    end_date_exp_3 = models.DateField(blank=True, null=True)
    additional_study = models.CharField(max_length=1024, null=True, blank=True)
    language_skill = models.CharField(max_length=1024, null=True, blank=True)
    computer_skill = models.CharField(max_length=1024, null=True, blank=True)
    additional_skill = models.CharField(max_length=1024, null=True, blank=True)
    salary = models.CharField(max_length=100, null=True, blank=True)
    additional_information = models.TextField(max_length=100, null=True, blank=True)
    institution = models.CharField(max_length=100, null=True, blank=True)

    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def get_index_model():
        from b24online.search_indexes import ResumeIndex
        return ResumeIndex

    def reindex(self):
        reindex_instance(self)

    def get_absolute_url(self):
        return reverse('resume:detail', args=[self.slug, self.pk])

    def has_perm(self, user):
        if not user.is_authenticated() or user.is_anonymous():
            return False

        return user.is_commando or user.is_superuser or self.user == user