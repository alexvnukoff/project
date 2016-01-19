from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from mptt.admin import MPTTModelAdmin
from django.utils.translation import ugettext_lazy as _
from polymorphic_tree.admin import PolymorphicMPTTChildModelAdmin, \
    PolymorphicMPTTParentModelAdmin
from b24online.models import (B2BProductCategory, Country, Branch, Company,
                              Organization, Chamber, BannerBlock, B2BProduct,
                              RegisteredEventStats, RegisteredEvent, User)


class BaseChildAdmin(PolymorphicMPTTChildModelAdmin):
    GENERAL_FIELDSET = (None, {
        'fields': ('parent', 'name'),
    })

    base_model = Organization

    base_fieldsets = (
        GENERAL_FIELDSET,
    )


# Create the parent admin that combines it all:

class TreeNodeParentAdmin(PolymorphicMPTTParentModelAdmin):
    base_model = Organization
    child_models = (
        (Company, BaseChildAdmin),
        (Chamber, BaseChildAdmin)
    )

    class Media:
        css = {
            'all': ('admin/treenode/admin.css',)
        }


class CompanyAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('id', 'name', 'slug', 'director', 'company_paypal_account',)
    search_fields = ['name', 'slug', 'director', 'company_paypal_account', ]


class RegisteredEventAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'is_unique', 'ip_address', 'user_agent',
                    'registered_at', 'geo_info']
    list_per_page = 20
    list_filter = ['is_unique', 'registered_at']


class RegisteredEventStatsAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'unique_amount', 'total_amount',
                    'registered_at']
    list_per_page = 20
    list_filter = ['registered_at']


class B24UserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('email',)}),
        (_('Permissions'), {'fields': ('is_active',)}),
        (_('Important dates'), {'fields': ('date_joined', )}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'last_login', 'date_joined', 'is_active', 'is_admin')
    list_filter = ('is_superuser', 'is_active', 'groups')
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)
    change_form_template = 'loginas/change_form.html'

admin.site.register(User, B24UserAdmin)
admin.site.register(B2BProductCategory, MPTTModelAdmin)
admin.site.register(Country, ModelAdmin)
admin.site.register(Branch, MPTTModelAdmin)
admin.site.register(Organization, TreeNodeParentAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Chamber, ModelAdmin)
admin.site.register(BannerBlock, ModelAdmin)
admin.site.register(B2BProduct, ModelAdmin)
admin.site.register(RegisteredEvent, RegisteredEventAdmin)
admin.site.register(RegisteredEventStats, RegisteredEventStatsAdmin)
