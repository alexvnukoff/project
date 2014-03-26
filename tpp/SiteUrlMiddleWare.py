from django.contrib.sites.models import Site
from django.conf import settings
from threading import current_thread
import os
from django.http import HttpResponseBadRequest



class SiteUrlMiddleWare:

    def process_request(self, request):

        current_domain = request.META.get('HTTP_HOST', False)

        if current_domain is False:
            return HttpResponseBadRequest()
        
        if current_domain[:4] == "www":
            current_domain = current_domain[4:]
        try:
            site = Site.objects.get(domain=current_domain)

            settings.SITE_ID = site.pk
            settings.ROOT_URLCONF = str(site.name)+".urls"
            request.urlconf = str(site.name)+".urls"
            settings.TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), '..', 'templates').replace('\\', '/'),
                     os.path.join(os.path.dirname(__file__), '..', str(site.name)+'/templates').replace('\\', '/'), )


        except Site.DoesNotExist:
            settings.SITE_ID = 1
            request.urlconf = "tppcenter.urls"
            settings.ROOT_URLCONF = "tppcenter.urls"
            settings.TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), '..', 'templates').replace('\\', '/'),
                     os.path.join(os.path.dirname(__file__), '..', 'tppcenter/templates').replace('\\', '/'), )




class GlobalRequest(object):
    _requests = {}

    @staticmethod
    def get_request():
        try:
                return GlobalRequest._requests[current_thread()]
        except KeyError:
                return None

    def process_request(self, request):
        GlobalRequest._requests[current_thread()] = request

    def process_response(self, request, response):
        # Cleanup
        thread = current_thread()
        try:
            del GlobalRequest._requests[thread]
        except KeyError:
            pass
        return response

def get_request():
    return GlobalRequest.get_request()



class setCurrCompany:

    def process_request(self, request):
        from appl.models import Organization

        if request.user.is_authenticated():
            #Set curr company on tppcenter
            newCompany = request.GET.get('current-org', None)

            if newCompany is not None:
                user_groups = request.user.groups.values_list('pk', flat=True)

                if newCompany == 'cabinet':
                    request.session['current_company'] = False
                elif newCompany:

                    company = Organization.objects.filter(community__in=user_groups, pk=newCompany)

                    if company.exists():
                        try:
                            request.session['current_company'] = int(newCompany)
                        except ValueError:
                            request.session['current_company'] = False
                    else:
                        request.session['current_company'] = False

