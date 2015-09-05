from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from b24online.models import B2BProductCategory

admin.site.register(B2BProductCategory, MPTTModelAdmin)
