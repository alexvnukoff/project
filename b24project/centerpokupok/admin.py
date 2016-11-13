from django.contrib import admin
from django.contrib.admin import ModelAdmin
from mptt.admin import MPTTModelAdmin
from centerpokupok.models import B2CProductCategory, B2CProduct, UserBasket, BasketItem


class UserBasketAdmin(admin.ModelAdmin):
    list_display = ['user_uuid', 'site_id', 'currency', 'paypal', 'checked_out', 'created',]
    readonly_fields = ['user_uuid', 'site_id', 'currency', 'paypal', 'created',]


class ItemBasketAdmin(admin.ModelAdmin):
    list_display = ['basket', 'product', 'quantity', ]
    readonly_fields = ['basket', 'product', 'quantity', ]


class B2CProductAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ['name', 'company',  'created_at', 'created_by', ]
    date_hierarchy = 'created_at'
    raw_id_fields = ('categories', 'producer', 'company', 'created_by', 'updated_by',)


admin.site.register(B2CProductCategory, MPTTModelAdmin)
admin.site.register(B2CProduct, B2CProductAdmin)
admin.site.register(UserBasket, UserBasketAdmin)
admin.site.register(BasketItem, ItemBasketAdmin)
