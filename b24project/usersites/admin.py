from django.contrib import admin
from django.contrib.admin import ModelAdmin
from usersites.models import ExternalSiteTemplate, UserSite, UserSiteTemplate

class UserSiteTemplateAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('name', 'folder_name',)

class UserSiteAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('site', 'organization',)
    raw_id_fields = [
            'organization',
            'site',
            'created_by',
            'updated_by'
            ]

admin.site.register(ExternalSiteTemplate, ModelAdmin)
admin.site.register(UserSite, UserSiteAdmin)
admin.site.register(UserSiteTemplate, UserSiteTemplateAdmin)
