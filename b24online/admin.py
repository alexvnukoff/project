from django.contrib import admin
from django.contrib.admin import ModelAdmin
from mptt.admin import MPTTModelAdmin
from polymorphic_tree.admin import PolymorphicMPTTChildModelAdmin, PolymorphicMPTTParentModelAdmin

from b24online.models import B2BProductCategory, Country, Branch, Company, Organization, Chamber, BannerBlock


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

admin.site.register(B2BProductCategory, MPTTModelAdmin)
admin.site.register(Country, ModelAdmin)
admin.site.register(Branch, MPTTModelAdmin)
admin.site.register(Organization, TreeNodeParentAdmin)
admin.site.register(Company, ModelAdmin)
admin.site.register(Chamber, ModelAdmin)
admin.site.register(BannerBlock, ModelAdmin)
