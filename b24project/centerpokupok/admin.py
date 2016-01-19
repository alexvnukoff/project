from django.contrib import admin
from django.contrib.admin import ModelAdmin
from mptt.admin import MPTTModelAdmin
from centerpokupok.models import B2CProductCategory, B2CProduct, UserBasket, BasketItem


class UserBasketAdmin(admin.ModelAdmin):

    list_display    = ['user_uuid', 'site_id', 'currency', 'paypal', 'checked_out', 'created',]
    readonly_fields = ['user_uuid', 'site_id', 'currency', 'paypal', 'created',]


class ItemBasketAdmin(admin.ModelAdmin):

    list_display    = ['basket', 'product', 'quantity', ]
    readonly_fields = ['basket', 'product', 'quantity', ]


class MyModelAdmin(MPTTModelAdmin):
    def get_queryset(self, request):
             return B2CProductCategory.foradmin.all()


admin.site.register(B2CProductCategory, MyModelAdmin)
admin.site.register(B2CProduct, ModelAdmin)
admin.site.register(UserBasket, UserBasketAdmin)
admin.site.register(BasketItem, ItemBasketAdmin)