# -*- encoding: utf-8 -*-

import json 
import logging
import datetime

from django.core.cache import cache
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from django.views.generic import TemplateView

from appl import func
from b24online.models import (Organization, Company, Tender, 
    RegisteredEvent, B2BProduct)
from centerpokupok.models import B2CProduct

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


class RegisteredEventsList(TemplateView):
    template_name = 'b24online/Analytic/registered_events_list.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(request, **kwargs)
        return self.render_to_response(context)
                    
    def get_context_data(self, request, **kwargs):
        context = super(RegisteredEventsList, self)\
            .get_context_data(**kwargs)

        # Current organization and products
        organization = request.session.get('current_company', None)
        data_grid = []
        start_date = finish_date = datetime.date.today()
        if organization:
            if True:
                b2c_products = B2CProduct.get_active_objects()\
                    .filter(company_id=organization)
        return context
