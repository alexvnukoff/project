from django.contrib import admin
from django.contrib.admin import ModelAdmin
from mptt.admin import MPTTModelAdmin
from centerpokupok.models import B2CProductCategory, B2CProduct, B2CBasket


class B2CBasketAdmin(admin.ModelAdmin):

    list_display    = ['user_id', 'site_name', 'ordered', 'created', 'product_id', 'quantity',]
    readonly_fields = ['user_id', 'quantity', 'site_name',]


admin.site.register(B2CProductCategory, MPTTModelAdmin)
admin.site.register(B2CProduct, ModelAdmin)
admin.site.register(B2CBasket, B2CBasketAdmin)