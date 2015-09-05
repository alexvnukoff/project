from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from centerpokupok.models import B2CProductCategory

admin.site.register(B2CProductCategory, MPTTModelAdmin)
