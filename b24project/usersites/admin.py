from django.contrib import admin
from django.contrib.admin import ModelAdmin
from usersites.models import ExternalSiteTemplate, UserSite, UserSiteTemplate

admin.site.register(ExternalSiteTemplate, ModelAdmin)
admin.site.register(UserSite, ModelAdmin)
admin.site.register(UserSiteTemplate, ModelAdmin)
