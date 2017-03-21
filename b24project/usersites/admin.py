# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from usersites.models import (ExternalSiteTemplate, UserSite, UserSiteTemplate,
                    UserSiteSchemeColor, LandingPage)
from django import forms
from django.conf import settings


class UserSiteSchemeColorInline(admin.StackedInline):
    model = UserSiteSchemeColor
    extra = 2


class UserSiteTemplateAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('name', 'folder_name',)

    inlines = ( UserSiteSchemeColorInline, )


class UserSiteAdminForm(forms.ModelForm):
    class Meta:
        model = UserSite
        fields = ('__all__')

    def __init__(self, *args, **kwargs):
        super(UserSiteAdminForm, self).__init__(*args, **kwargs)
        if self.instance.user_template:
            self.fields['color_template'].queryset = self.instance.user_template.colors.all()

    languages = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, required=False, choices=settings.LANGUAGES)


class UserSiteAdmin(admin.ModelAdmin):
    save_on_top = True
    form = UserSiteAdminForm
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
admin.site.register(LandingPage, ModelAdmin)
