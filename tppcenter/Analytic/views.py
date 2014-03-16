__author__ = 'user'

from django.shortcuts import render_to_response
from django.template import RequestContext

def main(request):

    #current_organization = request.session.get('current_company', False)

    #if current_organization is False:
    #    return render_to_response("permissionDen.html")

    #org = Organization.objects.get(pk=current_organization)

    #perm_list = org.getItemInstPermList(request.user)

    #if 'view_analytic' not in perm_list:
    #     return render_to_response("permissionDenied.html")

    templateParams = {}

    #if getattr(org, 'Tpp', False):
    #    templateParams['tpp'] = org.pk
    #else:
    #    templateParams['company'] = org.pk

    return render_to_response("Analytic/main.html", templateParams, context_instance=RequestContext(request))