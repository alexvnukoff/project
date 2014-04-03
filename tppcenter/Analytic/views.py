from appl import func
from appl.models import Organization
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, HttpResponse

import json

@login_required(login_url='/login/')
def main(request):
    '''
        Main analytic page
    '''

    current_organization = request.session.get('current_company', False)

    if current_organization is False:
        return HttpResponseRedirect(reverse('denied'))

    current_organization = Organization.objects.get(pk=current_organization)

    templateParams = {'current_company': current_organization.getAttributeValues("NAME")}

    if func.organizationIsCompany(current_organization):
        templateParams['tpp'] = current_organization.getTpp()


    return render_to_response("Analytic/main.html", templateParams, context_instance=RequestContext(request))

@login_required(login_url='/login/')
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
