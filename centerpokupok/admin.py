from django.contrib import admin
from django.contrib.admin import ModelAdmin
from mptt.admin import MPTTModelAdmin
from centerpokupok.models import B2CProductCategory, B2CProduct

admin.site.register(B2CProductCategory, MPTTModelAdmin)
admin.site.register(B2CProduct, ModelAdmin)