from django.contrib import admin
from django.contrib.admin import ModelAdmin
from mptt.admin import MPTTModelAdmin
from polymorphic_tree.admin import PolymorphicMPTTChildModelAdmin, \
                                  PolymorphicMPTTParentModelAdmin

from b24online.models import B2BProductCategory, Country, Branch, Company, \
                           Organization, Chamber, BannerBlock, B2BProduct


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
    search_fields = ['name', 'slug', 'director', 'company_paypal_account',]


admin.site.register(B2BProductCategory, MPTTModelAdmin)
admin.site.register(Country, ModelAdmin)
admin.site.register(Branch, MPTTModelAdmin)
admin.site.register(Organization, TreeNodeParentAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Chamber, ModelAdmin)
admin.site.register(BannerBlock, ModelAdmin)
admin.site.register(B2BProduct, ModelAdmin)
