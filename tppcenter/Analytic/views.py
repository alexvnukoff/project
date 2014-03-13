__author__ = 'user'

from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.conf import settings
from appl import func
from appl.models import Notification, Organization

def main(request):

    #current_organization = request.session.get('current_company', False)

    #if current_organization is False:
    #    return render_to_response("permissionDen.html")

    #org = Organization.objects.get(pk=current_organization)

    #perm_list = org.getItemInstPermList(request.user)

    #if 'view_analytic' not in perm_list:
    #     return render_to_response("permissionDenied.html")

    bRight = func.getBannersRight(request, ['Right 1', 'Right 2'], settings.SITE_ID, 'AdvBanner/banners.html')
    bLeft = func.getBannersRight(request, ['Left 1', 'Left 2', 'Left 3'], settings.SITE_ID, 'AdvBanner/banners.html')


    templateParams = {}

    #if getattr(org, 'Tpp', False):
    #    templateParams['tpp'] = org.pk
    #else:
    #    templateParams['company'] = org.pk

    return render_to_response("Analytic/main.html", templateParams)