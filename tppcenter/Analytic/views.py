from django.core.cache import cache
from django.db.models import Q
from appl import func
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, HttpResponse

import json
from b24online.models import Organization, Company, Tender


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

    return render_to_response("Analytic/main.html", template_params, context_instance=RequestContext(request))


@login_required
def getAnalytic(request):
    '''
        Get analytic of current organization
    '''

    current_company = request.session.get('current_company', False)

    if current_company is False:
        return HttpResponseRedirect(reverse('denied'))

    params = {'dimensions': 'ga:dimension2'}

    if func.organizationIsCompany(current_company):
        params['filters'] = 'ga:dimension1==' + str(current_company)
    else:
        params['filters'] = 'ga:dimension3==' + str(current_company)

    analytic = func.getAnalytic(params)

    result = {}

    if analytic:
        result = [{'type': row[0], 'count': row[1]} for row in analytic]

    return HttpResponse(json.dumps(result))
