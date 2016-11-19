# -*- encoding: utf-8 -*-

from celery import shared_task
from celery.utils.log import get_task_logger

from b24online import utils
from b24online.models import B2BProduct, BusinessProposal, InnovationProject, News, Tender, Exhibition, \
    Organization
from b24online.utils import upload_to_S3

logger = get_task_logger('debug.core.tasks')

from centerpokupok.models import B2CProduct
from jobs.models import Requirement
from usersites.models import UserSite


@shared_task
def upload_file(*args):
    upload_to_S3(*args)


@shared_task
def upload_images(*args, base_bucket_path=""):
    utils.upload_images(*args, base_bucket_path=base_bucket_path)


@shared_task
def on_company_active_changed(org_id):
    org = Organization.objects.get(pk=org_id)
    querysets = (
        B2BProduct.objects.filter(company=org).exclude(is_active=not org.is_deleted),
        B2CProduct.objects.filter(company=org).exclude(is_active=not org.is_deleted),
        UserSite.objects.filter(organization=org).exclude(is_active=not org.is_deleted),
        BusinessProposal.objects.filter(organization=org).exclude(is_active=not org.is_deleted),
        InnovationProject.objects.filter(organization=org).exclude(is_active=not org.is_deleted),
        News.objects.filter(organization=org).exclude(is_active=not org.is_deleted),
        Tender.objects.filter(organization=org).exclude(is_active=not org.is_deleted),
        Exhibition.objects.filter(organization=org).exclude(is_active=not org.is_deleted),
        Requirement.objects.filter(vacancy__department__organization=org).exclude(is_active=not org.is_deleted)
    )

    for queryset in querysets:
        objects_to_reindex = list(queryset)
        updated = queryset.update(is_active=not org.is_deleted)

        if updated > 0:
            for obj in objects_to_reindex:
                reindex_method = getattr(obj, 'reindex', None)

                if reindex_method is not None:
                    reindex_method(is_active_changed=True)


@shared_task
def on_chamber_active_changed(org_id):
    org = Organization.objects.get(pk=org_id)
    querysets = (
        UserSite.objects.filter(organization=org).exclude(is_active=not org.is_deleted),
        BusinessProposal.objects.filter(organization=org).exclude(is_active=not org.is_deleted),
        InnovationProject.objects.filter(organization=org).exclude(is_active=not org.is_deleted),
        News.objects.filter(organization=org).exclude(is_active=not org.is_deleted),
        Tender.objects.filter(organization=org).exclude(is_active=not org.is_deleted),
        Exhibition.objects.filter(organization=org).exclude(is_active=not org.is_deleted),
        Requirement.objects.filter(organization=org).exclude(is_active=not org.is_deleted)
    )

    for queryset in querysets:
        updated = queryset.update(is_active=not org.is_deleted)

        if updated > 0:
            for obj in queryset:
                reindex_method = getattr(obj, 'reindex', None)

                if reindex_method is not None:
                    reindex_method(is_active_changed=True)
