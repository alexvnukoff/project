from django.db import models

class L_User(models.Model):
    username = models.CharField(max_length=1024, unique=True)
    is_active = models.BooleanField()
    first_name = models.CharField(max_length=1024)
    last_name = models.CharField(max_length=1024)
    email = models.CharField(max_length=1024)
    btx_id = models.CharField(max_length=10, unique=True)
    update_date = models.DateField(null=True, blank=True)
    last_visit_date = models.DateField(null=True, blank=True)
    reg_date = models.DateField(null=True, blank=True)
