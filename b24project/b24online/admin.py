# -*- encoding: utf-8 -*-

import logging

from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect

from mptt.admin import MPTTModelAdmin
from polymorphic_tree.admin import PolymorphicMPTTChildModelAdmin, \
    PolymorphicMPTTParentModelAdmin
from b24online.models import (B2BProductCategory, Country, Branch, Company,
                              Organization, Chamber, BannerBlock, B2BProduct,
                              RegisteredEventStats, RegisteredEvent, User)
from b24online.stats.utils import convert_date

logger = logging.getLogger(__name__)


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


class RegisteredEventStatsAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'show_unique_amount', 
                    'show_total_amount', 'registered_at']
    list_per_page = 20
    list_filter = ['registered_at']

    def show_amount(self, object, cnt_type):
        """
        Return the the appropriate href to detailed stats.
        """
        object_kwargs = object.get_kwargs()
        object_kwargs.update({'cnt_type': cnt_type})
        return '<a href="{1}?date={2}">{0}</a>' . format(
            object.unique_amount,
            reverse('admin:event_stats_detail', kwargs=object_kwargs),
            object.registered_at.strftime('%Y-%m-%d'))

    def show_unique_amount(self, object):
        """
        For 'unique' counter.
        """
        return self.show_amount(object, 'unique')
    show_unique_amount.allow_tags = True
    show_unique_amount.short_description = _('Unique amount')

    def show_total_amount(self, object):
        """
        For 'total' counter.
        """
        return self.show_amount(object, 'total')
    show_total_amount.allow_tags = True
    show_total_amount.short_description = _('Total amount')

    def show_stats(self, request, event_type_id, content_type_id,
                   instance_id, cnt_type):
        logger.debug('Step 1')
        if 'date' in request.GET:
            registered_at = convert_date(request.GET['date'])
            logger.debug(registered_at)
        ## stats_item = RegisteredEventStats.objects.get_stats_item()
        logger.debug('Step 2')
        return HttpResponseRedirect(
            reverse('admin:b24online_registeredeventstats_changelist'))

    def get_urls(self):
        return patterns(
            '',
             url(r'^stats/(?P<event_type_id>\d+?)/(?P<content_type_id>\d+?)/'
                 r'(?P<instance_id>\d+?)/(?P<cnt_type>\w+?)/$',
                 self.show_stats,
                 name='event_stats_detail'),
        ) + super(RegisteredEventStatsAdmin, self).get_urls()


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
admin.site.register(RegisteredEventStats, RegisteredEventStatsAdmin)
