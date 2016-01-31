# -*- encoding: utf-8 -*-

import json 
import re
import logging
import datetime
from collections import OrderedDict

from django.core.cache import cache
from django.db.models import Q, Count, Sum
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response, HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext_lazy as _

from appl import func
from b24online.models import (Organization, Company, Tender, Exhibition,
    RegisteredEvent, RegisteredEventStats, RegisteredEventType, B2BProduct,
    InnovationProject, BusinessProposal)
from centerpokupok.models import B2CProduct
from b24online.Analytic.forms import SelectPeriodForm
from b24online.utils import get_current_organization
from b24online.stats.utils import process_stats_data

logger = logging.getLogger(__name__)

@login_required
def main(request):
    current_organization = request.session.get('current_company', False)

    if current_organization is False:
        return HttpResponseRedirect(reverse('denied'))

    current_organization = Organization.objects.get(pk=current_organization)

    template_params = {'current_company': current_organization.name}

    if current_organization.parent and isinstance(current_organization, Company):
        key = "analytic:main:chamber:%s" % current_organization.parent.pk
        template_params['chamber_events'] = cache.get(key)

        if not template_params['chamber_events']:
            org_filter = Q(organization=current_organization.parent) | Q(organization__parent=current_organization.parent)
            template_params['chamber_events'] = {
                'tenders': Tender.objects.filter(org_filter).count(),
                'proposals': Tender.objects.filter(org_filter).count(),
                'exhibitions': Tender.objects.filter(org_filter).count()
            }

            cache.set(key, template_params['chamber_events'], 60 * 60 * 24)

    return render_to_response("b24online/Analytic/main.html", template_params, context_instance=RequestContext(request))


@login_required
def get_analytic(request):
    """
        Get analytic of current organization
    """

    current_company = request.session.get('current_company', None)

    if not current_company:
        return HttpResponseRedirect(reverse('denied'))

    params = {'dimensions': 'ga:dimension2'}

    if Company.objects.filter(pk=current_company).exists():
        params['filters'] = 'ga:dimension1==' + str(current_company)
    else:
        params['filters'] = 'ga:dimension3==' + str(current_company)

    analytic = func.get_analytic(params)

    result = {}

    if analytic:
        result = [{'type': row[0], 'count': row[1]} for row in analytic]

    return HttpResponse(json.dumps(result))


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
        try:
            instance = model_class.objects.get(pk=instance_id)
        except model_class.DoesNotExist:
            raise Http404

        context.update({'event_type_id': event_type.pk,
            'event_type': event_type,
            'content_type_id': content_type.pk, 
            'instance_type': model_name, 
            'instance': instance})

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
                event_type_id=event_type_id,
                object_id=instance_id)\
            .values('registered_at')\
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
        logger.debug(data_grid)
                
        context.update({
            'form': form,
            'date_limits': form.date_limits(),
            'date_range': date_range,
            'instance_data': data_grid,
            'instance_id': instance_id,
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
        if all((event_type_id, content_type_id, instance_id, 
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
                    try:
                        instance = model_class.objects.get(pk=instance_id)
                    except model_class.DoesNotExist:
                        break

                    context.update({'event_type': event_type, 
                        'instance_type': model_name, 
                        'instance': instance,
                        'xdate': xdate})
                
                    try:
                        stats = RegisteredEventStats.objects.filter(
                            event_type_id=event_type_id, 
                            content_type_id=content_type_id, 
                            object_id=instance_id,
                            registered_at=xdate)[0]
                    except IndexError:
                        pass
                    else:
                        data_grid = stats.get_extra_info(cnt_type)
                        context['data_grid'] = data_grid
                    break
        return context


class RegisteredEventStatsView(TemplateView):
    template_name = 'b24online/Analytic/registered_event_stats.html'
    form_class = SelectPeriodForm

    PROCESSED_MODELS = (
        (B2BProduct, 'company_id'),
        (B2CProduct, 'company_id'),
        (BusinessProposal, 'organization_id'),
        (InnovationProject, 'organization_id'),
        (Tender, 'organization_id'),
        (Exhibition, 'organization_id'),
    )
    
    STATS_ITEMS = (
        ('B2BProduct', _('B2B Products')),
        ('B2CProduct', _('B2C Products')),
        ('BusinessProposal', _('Business Proposals')),
        ('InnovationProject', _('Innovation Projects')),
        ('Tender', _('Tenders')),
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
        for item_model, org_field_name in cls.PROCESSED_MODELS:
            content_type = ContentType.objects\
                .get_for_model(item_model)
            model_class = content_type.model_class()
            model_name = model_class.__name__
            content_type_ids[model_name] = content_type.pk                 
            company_filter = {org_field_name: current_organization}
            ids = [item.id for item in item_model.objects\
                .filter(**company_filter)]
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
        event_types = OrderedDict()
        for content_type_id, data_1 in data.items():
            for item_id, data_2 in data_1.items():
                for event_type_id, _ in data_2.items():
                    try:
                        event_type = RegisteredEventType.objects\
                            .get(id=event_type_id)
                    except RegisteredEventType.DoesNotExist:
                        continue
                    else:
                        event_types[event_type_id] = event_type

        raw_data_grid = {}
        for content_type_id, data_1 in data.items():
            try:
                content_type = ContentType.objects.get(pk=content_type_id)
            except ContentType.DoesNotExist:
                continue
            model_class = content_type.model_class()
            model_name = model_class.__name__
            
            common_stats = OrderedDict([(event_type_id, {'unique': 0, 'total': 0}) \
                for event_type_id, _ in event_types.items()])
            detail_stats = []
            for item_id, data_2 in data_1.items():
                try:
                    item = model_class.objects.get(pk=item_id)
                except model_class.DoesNotExist:
                    continue
                else:
                    _data = OrderedDict()
                    for event_type_id, event_type in event_types.items():
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
        
        null_data = {'common': OrderedDict([(event_type_id, {'unique': 0, 'total': 0}) \
                for event_type_id, _ in event_types.items()]), 
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
            'event_types': [(k, v) for k, v in event_types.items()],
        })
        return context
