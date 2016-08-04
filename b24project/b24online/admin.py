# -*- encoding: utf-8 -*-

import logging

from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db.models import Q, Sum
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from mptt.admin import MPTTModelAdmin
from polymorphic_tree.admin import PolymorphicMPTTChildModelAdmin, \
    PolymorphicMPTTParentModelAdmin

from b24online.Analytic.forms import SelectPeriodForm
from b24online.models import (B2BProductCategory, Country, Branch, Company,
                              Organization, Chamber, BannerBlock, B2BProduct,
                              RegisteredEventStats, RegisteredEventType, User,
                              Profile, BusinessProposal,
                              BusinessProposalCategory, DealOrder, Deal,
                              DealItem, StaffGroup, PermissionsExtraGroup,
                              MessageChat, Message, Producer,
                              Questionnaire, Question, Recommendation,
                              AdditionalPage, LeadsStore, Banner)
from b24online.stats.utils import convert_date
from centerpokupok.models import B2CProduct
from tpp.DynamicSiteMiddleware import get_current_site

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
    form_class = SelectPeriodForm

    def show_amount(self, object, cnt_type):
        """
        Return the the appropriate href to detailed stats.
        """
        object_kwargs = object.get_kwargs()
        object_kwargs.update({'cnt_type': cnt_type})
        amount = object.unique_amount if cnt_type == 'unique' \
            else object.total_amount
        return '<a href="{1}?date={2}">{0}</a>'.format(
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

    def show_stats_detail(self, request, event_type_id, content_type_id,
                          instance_id, cnt_type):
        site = get_current_site()
        if 'date' in request.GET:
            registered_at = convert_date(request.GET['date'])
            try:
                stats = RegisteredEventStats.objects.get(
                    event_type_id=event_type_id,
                    # site_id=site.pk,
                    content_type_id=content_type_id,
                    object_id=instance_id,
                    registered_at=registered_at)
            except RegisteredEventStats.DoesNotExist:
                return HttpResponseRedirect(
                    reverse('admin:b24online_registeredeventstats_changelist'))
            else:
                data_grid = stats.get_extra_info(cnt_type)
                context = {
                    'data_grid': data_grid,
                    'item': stats,
                    'has_permission': True,
                    'opts': RegisteredEventStats._meta,
                }
                return render_to_response(
                    'admin/show_stats_detail.html',
                    context,
                    context_instance=RequestContext(request))

    def show_stats(self, request):
        site = get_current_site()
        b2c_content_type = ContentType.objects.get_for_model(B2CProduct)
        b2b_content_type = ContentType.objects.get_for_model(B2BProduct)

        validate_by_form = False
        if 'start_date' in request.GET and 'end_date' in request.GET:
            form = self.form_class(data=request.GET)
            if form.is_valid():
                validate_by_form = True
        else:
            form = self.form_class()

        data_grid = []
        event_types = RegisteredEventType.objects.order_by('id')
        for event_type in event_types:
            qs = RegisteredEventStats.objects.filter(
                Q(event_type_id=event_type.pk) \
                & (Q(content_type_id=b2c_content_type) \
                   | Q(content_type_id=b2b_content_type))) \
                .values('content_type_id', 'object_id') \
                .annotate(unique=Sum('unique_amount'),
                          total=Sum('total_amount')) \
                .order_by('-unique')
            if validate_by_form:
                qs = form.filter(qs)
            qs = qs[:20]
            data_grid.append((event_type, qs))
        context = {
            'event_types': event_types,
            'data_grid': data_grid,
            'form': form,
            'opts': RegisteredEventStats._meta,
        }

        return render_to_response(
            'admin/show_stats.html',
            context,
            context_instance=RequestContext(request))

    def get_urls(self):
        return [
                   url(r'^stats/$',
                       self.show_stats,
                       name='event_stats'),
                   url(r'^stats/(?P<event_type_id>\d+?)/(?P<content_type_id>\d+?)/'
                       r'(?P<instance_id>\d+?)/(?P<cnt_type>\w+?)/$',
                       self.show_stats_detail,
                       name='event_stats_detail'),
               ] + super(RegisteredEventStatsAdmin, self).get_urls()


class B24UserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('email',)}),
        (_('Permissions'), {'fields': ('is_active', 'user_permissions')}),
        (_('Important dates'), {'fields': ('date_joined',)}),
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


class QuestionAdmin(admin.ModelAdmin):
    list_filter = ('questionnaire',)


class LeadsAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('organization', 'email', 'realname', 'username', 'created_at',)
    search_fields = ['subject', 'message',]
    raw_id_fields = ('organization', 'username', )


class BannerAdmin(admin.ModelAdmin):
    list_filter = ('site', 'organization')
    search_fields = ['site',]

admin.site.register(User, B24UserAdmin)
admin.site.register(B2BProductCategory, MPTTModelAdmin)
admin.site.register(Country, ModelAdmin)
admin.site.register(Branch, MPTTModelAdmin)
admin.site.register(Organization, TreeNodeParentAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Chamber, ModelAdmin)
admin.site.register(BannerBlock, ModelAdmin)
admin.site.register(B2BProduct, ModelAdmin)
admin.site.register(Profile, ModelAdmin)
admin.site.register(BusinessProposal, ModelAdmin)
admin.site.register(BusinessProposalCategory, ModelAdmin)
admin.site.register(RegisteredEventStats, RegisteredEventStatsAdmin)
admin.site.register(DealOrder, ModelAdmin)
admin.site.register(Deal, ModelAdmin)
admin.site.register(DealItem, ModelAdmin)
admin.site.register(StaffGroup, ModelAdmin)
admin.site.register(PermissionsExtraGroup, ModelAdmin)
admin.site.register(MessageChat, ModelAdmin)
admin.site.register(Message, ModelAdmin)
admin.site.register(Producer, ModelAdmin)
admin.site.register(Questionnaire, ModelAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Recommendation, ModelAdmin)
admin.site.register(AdditionalPage, ModelAdmin)
admin.site.register(LeadsStore, LeadsAdmin)
admin.site.register(Banner, BannerAdmin)
