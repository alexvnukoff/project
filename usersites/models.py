from django.db import models
from b24online.models import Organization
from core.models import User


class UserSite(models.Model):
    organization = models.ForeignKey(Organization)
    is_active = models.BooleanField(default=True, db_index=True)

    created_by = models.ForeignKey(User, related_name='%(class)s_create_user')
    updated_by = models.ForeignKey(User, related_name='%(class)s_update_user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

