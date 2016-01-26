from django.contrib import admin
from django.contrib.admin import ModelAdmin
from usersites.models import ExternalSiteTemplate, UserSite, UserSiteTemplate

class UserSiteTemplateAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('name', 'folder_name',)

admin.site.register(ExternalSiteTemplate, ModelAdmin)
admin.site.register(UserSite, ModelAdmin)
admin.site.register(UserSiteTemplate, UserSiteTemplateAdmin)
