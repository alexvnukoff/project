# -*- encoding: utf-8 -*-

import datetime
import logging
import re
from collections import OrderedDict

from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db.models import Q, Sum
from django.http import HttpResponseRedirect, Http404
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView

from b24online.Analytic.forms import SelectPeriodForm
from b24online.models import (Company, Tender, Exhibition,
                              RegisteredEventStats, RegisteredEventType, B2BProduct,
                              InnovationProject, BusinessProposal)
from b24online.utils import get_current_organization
from centerpokupok.models import B2CProduct

logger = logging.getLogger(__name__)

PROCESSED_MODELS = (
    (B2BProduct, 'company_id'),
    (B2CProduct, 'company_id'),
    (BusinessProposal, 'organization_id'),
    (InnovationProject, 'organization_id'),
    (Tender, 'organization_id'),
    (Exhibition, 'organization_id'),
)


class RegisteredEventStatsDetailView(TemplateView):
    template_name = 'b24online/Analytic/registered_event_stats_detail.html'
    form_class = SelectPeriodForm

    def dispatch(self, *args, **kwargs):
        return super(RegisteredEventStatsDetailView, self)\
            .dispatch(*args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        """
        Add the request for processing in args.
        """
        context = self.get_context_data(request, **kwargs)
        redirect_url = context.get('redirect_url')
        if redirect_url:
            return HttpResponseRedirect(redirect_url)
        return self.render_to_response(context)
                    
    def get_context_data(self, request, **kwargs):
        context = {}

        event_type_id, content_type_id, instance_id, cnt_type = \
            map(lambda x: self.kwargs.get(x), 
                ('event_type_id', 'content_type_id', 
                'instance_id', 'cnt_type'))
        current_organization = get_current_organization(request)
        try:
            event_type = RegisteredEventType.objects.get(id=event_type_id)
        except RegisteredEventType.DoesNotExist:
            raise Http404
            
        try:
            content_type = ContentType.objects.get(pk=content_type_id)
        except ContentType.DoesNotExist:
            raise Http404
        model_class = content_type.model_class()
        model_name = model_class._meta.verbose_name \
            or model_class.__name__
            
        if instance_id:
            try:
                instance = model_class.objects.get(pk=instance_id)
            except model_class.DoesNotExist:
                raise Http404
        else:
            instance = None

        qs = RegisteredEventStats.objects.all()
        if 'start_date' in request.GET and 'end_date' in request.GET: 
            form = self.form_class(data=request.GET)
            if form.is_valid():
                qs = form.filter(qs)
        else:
            form = self.form_class()
            qs = form.filter(qs)
            
        date_range = list(form.date_range())


        qs = qs.filter(content_type_id=content_type_id, 
                event_type_id=event_type_id)
        if instance_id:
            qs = qs.filter(object_id=instance_id)
        org_field_name = dict(PROCESSED_MODELS).get(model_class)
        if org_field_name:
            if model_class in (B2BProduct, B2CProduct):
                if isinstance(current_organization, Company):
                    org_ids = [current_organization.pk,]        
                else:
                    org_ids = [item.pk for item in
                        current_organization\
                            .get_descendants_for_model(Company)]
            else:
                org_ids = [current_organization.pk,] + \
                    [item.pk for item in current_organization\
                        .get_descendants()]
            organization_filter = {'%s__in' % org_field_name: org_ids}
            ids = [item.id for item in model_class.objects\
                .filter(**organization_filter)]
            if ids:
                qs = qs.filter(object_id__in=ids)

        qs = qs.values('registered_at')\
            .annotate(unique=Sum('unique_amount'), 
                total=Sum('total_amount'))\
            .order_by('registered_at') 

        # Build the data grid
        data = dict((item['registered_at'], {'unique': item['unique'], 
            'total': item['total']}) for item in qs)

        data_grid = []
        for registered_at, item in date_range:
            _data = data.get(registered_at, {'unique': 0, 'total': 0})
            _data.update({'date': registered_at})
            data_grid.append(_data)
                
        context.update({
            'form': form,
            'date_limits': form.date_limits(),
            'date_range': date_range,
            'event_type_id': event_type.pk,
            'event_type': event_type,
            'content_type_id': content_type.pk, 
            'instance_type': model_name, 
            'data_grid': data_grid,
            'instance_id': instance_id,
            'instance': instance,
        })
        return context


class RegisteredEventStatsDiagView(TemplateView):
    template_name = 'b24online/Analytic/registered_event_stats_diag.html'
    
    def get_context_data(self, **kwargs):
        date_re = re.compile('^(\d{4})-(\d{1,2})-(\d{1,2})$')
        context = super(RegisteredEventStatsDiagView, self)\
            .get_context_data(**kwargs)
        event_type_id, content_type_id, instance_id, cnt_type = \
            map(lambda x: self.kwargs.get(x), 
                ('event_type_id', 'content_type_id', 
                'instance_id', 'cnt_type'))
        data_str = self.request.GET.get('date', None)
        current_organization = get_current_organization(self.request)

        if all((event_type_id, content_type_id, 
           cnt_type, data_str)):
            _m = date_re.match(data_str)
            if _m:
                while True:
                    try:
                        xdate = datetime.date(*map(int, _m.groups()))                
                    except:
                        break

                    try:
                        event_type = RegisteredEventType.objects.get(id=event_type_id)
                    except RegisteredEventType.DoesNotExist:
                        break
                        
                    try:
                        content_type = ContentType.objects.get(pk=content_type_id)
                    except ContentType.DoesNotExist:
                        break
                    model_class = content_type.model_class()
                    model_name = model_class._meta.verbose_name \
                        or model_class.__name__
                    if instance_id:
                        try:
                            instance = model_class.objects.get(pk=instance_id)
                        except model_class.DoesNotExist:
                            break
                    else:
                        instance = None

                    context.update({'event_type': event_type, 
                        'instance_type': model_name, 
                        'instance': instance,
                        'xdate': xdate})

                    qs = RegisteredEventStats.objects.filter(
                        event_type_id=event_type_id, 
                        content_type_id=content_type_id,
                        registered_at=xdate)

                    if instance_id:
                        qs = qs.filter(object_id=instance_id)
                        stats = qs[0]
                        data_grid = stats.get_extra_info(cnt_type)
                    else:
                        org_field_name = dict(PROCESSED_MODELS).get(model_class)
                        if org_field_name:
                            if model_class in (B2BProduct, B2CProduct):
                                if isinstance(current_organization, Company):
                                    org_ids = [current_organization.pk,]        
                                else:
                                    org_ids = [item.pk for item in
                                        current_organization\
                                            .get_descendants_for_model(Company)]
                            else:
                                org_ids = [current_organization.pk,] + \
                                    [item.pk for item in current_organization\
                                        .get_descendants()]
                            organization_filter = {'%s__in' % org_field_name: org_ids}
                            ids = [item.id for item in model_class.objects\
                                .filter(**organization_filter)]
                            if ids:
                                qs = qs.filter(object_id__in=ids)

                        _data = {}
                        for stats in qs:
                            _data_1 = stats.get_extra_info(cnt_type)
                            for country, amount, city_distrib in \
                                stats.get_extra_info(cnt_type):
                                if country in _data:
                                    _data[country]['amount'] += amount
                                    for k, v in city_distrib:
                                        if k in _data[country]['cities']:
                                            _data[country]['cities'][k] += v
                                        else:
                                            _data[country]['cities'][k] = v 
                                else:
                                    _data.setdefault(country, {})['amount'] = amount
                                    _data[country]['cities'] =\
                                        dict(city_distrib) if city_distrib else {}
                        data_grid = []
                        if _data:
                            for k, v in _data.items():
                                data_grid.append([k, v['amount'], 
                                    [(k1, v1) for k1, v1 in v['cities'].items()]])
                    context['data_grid'] = data_grid
                    break
        return context


class RegisteredEventStatsView(TemplateView):
    template_name = 'b24online/Analytic/registered_event_stats.html'
    form_class = SelectPeriodForm
    
    STATS_ITEMS = (
        ('B2BProduct', _('B2B Products')),
        ('B2CProduct', _('B2C Products')),
        ('BusinessProposal', _('Business Proposals')),
        ('InnovationProject', _('Innovation Projects')),
#        ('Tender', _('Tenders')),
        ('Exhibition', _('Exhibitions')),
        ('Main', _('Main')),
        ('Company', _('Companies')),
        )

    def dispatch(self, *args, **kwargs):
        return super(RegisteredEventStatsView, self).dispatch(*args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        """
        Add the request for processing in args.
        """
        context = self.get_context_data(request, **kwargs)
        redirect_url = context.get('redirect_url')
        if redirect_url:
            return HttpResponseRedirect(redirect_url)
        if self.request.is_ajax():
            self.template_name = \
                'b24online/Analytic/registered_event_stats_base.html'
        return self.render_to_response(context)
                    
    def get_context_data(self, request, **kwargs):
        cls = type(self)
        context = {}

        # Define selected organization (company)
        current_organization = get_current_organization(request)
        if not current_organization:
            return {'redirect_url': reverse('denied')}
        context.update({'current_company': current_organization.name})

        qs = RegisteredEventStats.objects.all()
        if 'start_date' in request.GET and 'end_date' in request.GET: 
            form = self.form_class(data=request.GET)
            if form.is_valid():
                qs = form.filter(qs)
        else:
            form = self.form_class()
            qs = form.filter(qs)

        date_range = list(form.date_range())
        
        # Construct the query
        qs_filters = None
        content_type_ids = {}
        for item_model, org_field_name in PROCESSED_MODELS:
            content_type = ContentType.objects\
                .get_for_model(item_model)
            model_class = content_type.model_class()
            model_name = model_class.__name__
            content_type_ids[model_name] = content_type.pk                 

            if item_model in (B2BProduct, B2CProduct):
                if isinstance(current_organization, Company):
                    org_ids = [current_organization.pk,]        
                else:
                    org_ids = [item.pk for item in
                        current_organization.get_descendants_for_model(Company)]
            else:
                org_ids = [current_organization.pk,] + \
                    [item.pk for item in current_organization.get_descendants()]

            organization_filter = {'%s__in' % org_field_name: org_ids}
            ids = [item.id for item in item_model.objects\
                .filter(**organization_filter)]

            qs_filter = Q(content_type_id=content_type) & \
                Q(object_id__in=ids)
            if not qs_filters:
                qs_filters = qs_filter
            else:
                qs_filters |= qs_filter

        qs = qs.filter(qs_filters)\
            .values('content_type_id', 'object_id', 'event_type_id')\
            .annotate(unique=Sum('unique_amount'), 
                total=Sum('total_amount'))\
            .order_by('content_type_id', 'object_id', 'event_type_id',
                '-unique')

        # Build the data grid
        data = OrderedDict()
        for item in qs:
            data.setdefault(item['content_type_id'], OrderedDict())\
                .setdefault(item['object_id'], OrderedDict())\
                .setdefault(item['event_type_id'], OrderedDict())\
                .update({'unique': item['unique'], 'total': item['total']})

        data_grid = {}
        event_types = [(item.id, item) \
            for item in RegisteredEventType.objects.order_by('id')]

        raw_data_grid = {}
        for content_type_id, data_1 in data.items():
            try:
                content_type = ContentType.objects.get(pk=content_type_id)
            except ContentType.DoesNotExist:
                continue
            model_class = content_type.model_class()
            model_name = model_class.__name__
            
            common_stats = OrderedDict([(event_type_id, {'unique': 0, 'total': 0}) \
                for event_type_id, _ in event_types])
            detail_stats = []
            for item_id, data_2 in data_1.items():
                try:
                    item = model_class.objects.get(pk=item_id)
                except model_class.DoesNotExist:
                    continue
                else:
                    _data = OrderedDict()
                    for event_type_id, event_type in event_types:
                        if event_type_id in data_2:
                            _stats = data_2[event_type_id]
                            common_stats[event_type_id]['unique'] += \
                                _stats['unique']
                            common_stats[event_type_id]['total'] += \
                                _stats['total']
                        else:
                            _stats = {'unique': 0, 'total': 0}
                        _data[event_type_id] = _stats
                    detail_stats.append((item, _data))
            raw_data_grid[model_name] = {
                'detailed': detail_stats,
                'common': common_stats}
        
        null_data = {'common': OrderedDict([
            (event_type_id, {'unique': 0, 'total': 0}) \
                for event_type_id, _ in event_types]), 
                'detailed': []}

        data_grid = []
        
        for item_key, item_name in cls.STATS_ITEMS:
            content_type_id = content_type_ids.get(item_key, None)
            if item_key in raw_data_grid:
                data_grid.append((content_type_id, item_key.lower(), item_name, 
                    raw_data_grid[item_key]))
            else:
                data_grid.append((content_type_id, item_key.lower(), 
                    item_name, null_data))
        
        context.update({
            'form': form,
            'date_limits': form.date_limits(),
            'date_range': date_range,
            'data_grid': data_grid,
            'event_types': event_types,
        })
        return context
