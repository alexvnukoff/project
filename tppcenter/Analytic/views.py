__author__ = 'user'

from django.shortcuts import render_to_response, HttpResponse
from django.template import RequestContext
import json
from appl import func
from appl.models import Organization, login_required

@login_required(login_url='/login/')
def main(request):

    current_organization = request.session.get('current_company', False)

    if current_organization is False:
        return render_to_response("permissionDen.html")

    org = Organization.objects.get(pk=current_organization)

    perm_list = org.getItemInstPermList(request.user)

    #if 'view_analytic' not in perm_list:
    #     return render_to_response("permissionDenied.html")

    if func.organizationIsCompany(org):
        templateParams = {'tpp': org.getTpp()}
    else:
        templateParams = {}
    #if getattr(org, 'Tpp', False):
    #    templateParams['tpp'] = org.pk
    #else:
    #    templateParams['company'] = org.pk

    return render_to_response("Analytic/main.html", templateParams, context_instance=RequestContext(request))

def getAnalytic(request):
    current_company = request.session.get('current_company', False)

    if current_company is False:
        return HttpResponse('')

    params = {'dimensions': 'ga:dimension2'}

    if func.organizationIsCompany(current_company):
        params['filters'] = 'ga:dimension1==' + str(current_company)
    else:
        params['filters'] = 'ga:dimension3==' + str(current_company)

    analytic = func.getAnalytic(params)

    result = {}

    if analytic:
        result = [{'type': row[0],'count': row[1]} for row in analytic]

    return HttpResponse(json.dumps(result))
