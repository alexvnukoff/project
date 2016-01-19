# -*- encoding: utf-8 -*-

from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse
from django.contrib.auth.admin import UserAdmin
from mptt.admin import MPTTModelAdmin
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
    search_fields = ['name', 'slug', 'director', 'company_paypal_account',]


class RegisteredEventAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'is_unique', 'ip_address', 'user_agent', 
                    'registered_at', 'geo_info']
    list_per_page = 20
    list_filter = ['is_unique', 'registered_at']    


class RegisteredEventStatsAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'show_unique_amount', 
                    'show_total_amount', 'registered_at']
    list_per_page = 20
    list_filter = ['registered_at']    

    def show_amount(self, object, cnt_type):
        object_kwargs = object.get_kwargs()
        object_kwargs.update({'cnt_type': cnt_type})
        return '<a href="{1}?date={2}">{0}</a>' . format(
            object.unique_amount,
            reverse('admin:event_stats_detail', kwargs=object_kwargs),
            object.registered_at.strftime('%Y-%m-%d'))

    def show_unique_amount(self, object):
        return self.show_amount(object, 'unique')
    show_unique_amount.allow_tags = True
    show_unique_amount.short_description = _('Unique amount')

    def show_total_amount(self, object):
        return self.show_amount(object, 'total')
    show_total_amount.allow_tags = True
    show_total_amount.short_description = _('Total amount')

    def show_stats(self, request):
        pass
                
    def get_urls(self):
        return patterns(
            '',
             url(r'^stats/(?P<event_type_id>\d+?)/(?P<content_type_id>\d+?)/'
                 r'(?P<instance_id>\d+?)/(?P<cnt_type>\w+?)/$',
                 self.show_stats,
                 name='event_stats_detail'),
        ) + super(RegisteredEventStatsAdmin, self).get_urls()


admin.site.register(User, UserAdmin)
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


