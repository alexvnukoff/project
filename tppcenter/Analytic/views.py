__author__ = 'user'

from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.conf import settings
from appl import func
from appl.models import Notification, Organization

def main(request):

    current_organization = request.session.get('current_company', False)
    current_organization =  221

    if current_organization is False:
        return render_to_response("permissionDen.html")

    org = Organization.objects.get(pk=current_organization)



    #perm_list = org.getItemInstPermList(request.user)

    #if 'view_analytic' not in perm_list:
    #     return render_to_response("permissionDenied.html")

    bRight = func.getBannersRight(request, ['Right 1', 'Right 2'], settings.SITE_ID, 'AdvBanner/banners.html')
    bLeft = func.getBannersRight(request, ['Left 1', 'Left 2', 'Left 3'], settings.SITE_ID, 'AdvBanner/banners.html')
    tops = func.getTops(request)

    user = request.user
    if user.is_authenticated():
        notification = Notification.objects.filter(user=request.user, read=False).count()
        if not user.first_name and not user.last_name:
            user_name = user.email
        else:
            user_name = user.first_name + ' ' + user.last_name
    else:
        user_name = None
        notification = None

    templateParams = {
        'user_name': user_name,
        'current_section': _('Analytic'),
        'notification': notification,
        'bannerRight': bRight,
        'bannerLeft': bLeft,
        'tops': tops
    }

    if getattr(org, 'Tpp', False):
        templateParams['tpp'] = org.pk
    else:
        templateParams['company'] = org.pk

    return render_to_response("Analytic/main.html", templateParams)