# -*- encoding: utf-8 -*-

import json 
import re
import logging
import datetime

from django.core.cache import cache
from django.db.models import Q, Count, Sum
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from appl import func
from b24online.models import (Organization, Company, Tender, Exhibition,
    RegisteredEvent, RegisteredEventStats, RegisteredEventType, B2BProduct)
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


class RegisteredEventStatsView(TemplateView):
    template_name = 'b24online/Analytic/registered_event_stats.html'
    form_class = SelectPeriodForm

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
        return self.render_to_response(context)
                    
    def get_context_data(self, request, **kwargs):
        context = {}

        # Define selected organization (company)
        current_organization = get_current_organization(request)
        if not current_organization:
            return {'redirect_url': reverse('denied')}
        context.update({'current_company': current_organization.name})

        ### Info about Tenders, Exhibition etc
        ### FIXME: delete, the block has been deleted from template
        ##if current_organization.parent and \
        ##    isinstance(current_organization, Company):
        ##   
        ##    key = "analytic:main:chamber:%s" % current_organization.parent.pk
        ##    context['chamber_events'] = cache.get(key)
        ##    if not context['chamber_events']:
        ##        org_filter = Q(organization=current_organization.parent) \
        ##            | Q(organization__parent=current_organization.parent)
        ##        context['chamber_events'] = {
        ##            'tenders': Tender.objects.filter(org_filter).count(),
        ##            'proposals': Tender.objects.filter(org_filter).count(),
        ##            'exhibitions': Exhibition.objects.filter(org_filter).count()
        ##        }
        ##        cache.set(key, context['chamber_events'], 60 * 60 * 24)

        # Filtered form
        qs = RegisteredEventStats.objects.all()
        if 'start_date' in request.GET and 'end_date' in request.GET: 
            form = self.form_class(data=request.GET)
            if form.is_valid():
                qs = form.filter(qs)
        else:
            form = self.form_class()
        date_range = list(form.date_range())

        # Form the qs
        b2c_content_type = ContentType.objects.get_for_model(B2CProduct)
        b2c_ids = [item.id for item in B2CProduct.get_active_objects()\
            .filter(company_id=current_organization)]

        b2b_content_type = ContentType.objects.get_for_model(B2BProduct)
        b2b_ids = [item.id for item in B2BProduct.get_active_objects()\
            .filter(company_id=current_organization)]

        qs = qs.filter(
            (Q(content_type_id=b2c_content_type) \
                & Q(object_id__in=b2c_ids)) | \
            (Q(content_type_id=b2b_content_type) \
                & Q(object_id__in=b2b_ids)))\
            .values('event_type_id', 'content_type_id', 'object_id', 
                'registered_at')\
            .annotate(unique=Sum('unique_amount'), 
                total=Sum('total_amount'))\
            .order_by('event_type_id', 'content_type_id', 
                'object_id', 'registered_at') 

        # Build the data grid
        data = {}
        for item in qs:
            data.setdefault(item['event_type_id'], {})\
                .setdefault(item['content_type_id'], {})\
                .setdefault(item['object_id'], {})\
                .setdefault(item['registered_at'], {})\
                .update({'unique': item['unique'], 'total': item['total']})
        data_grid = process_stats_data(data, date_range)

        context.update({
            'form': form,
            'date_range': date_range,
            'data_grid': data_grid,
            'organization': current_organization,
        })
        return context


class RegisteredEventStatsDetailView(TemplateView):
    template_name = 'b24online/Analytic/registered_event_stats_detail.html'
    
    def get_context_data(self, **kwargs):
        date_re = re.compile('^(\d{4})-(\d{1,2})-(\d{1,2})$')
        context = super(RegisteredEventStatsDetailView, self)\
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
