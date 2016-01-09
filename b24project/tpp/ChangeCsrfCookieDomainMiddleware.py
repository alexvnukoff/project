# -*- encoding: utf-8 -*-

"""
Change cookie domain to accept form sub domains( Lang sub domains )
"""

from django.conf import settings


class ChangeCsrfCookieDomainMiddleware:
    def process_request(self, request):
        current_domain = request.get_host().split(':')[0]
        current_domain_list = current_domain.split('.')

        if current_domain_list[0] in [item[0] for item in settings.LANGUAGES]:
            # Check the language prefix
            current_domain_list = current_domain_list[1:]
        if current_domain_list[0] == "www":
            # Check the 'www'-prefix
            current_domain_list = current_domain_list[1:]
        current_domain = "." . join([''] + current_domain_list)
        allowed = settings.ALLOWED_HOSTS
        if current_domain in allowed or "*" in allowed:
            settings.CSRF_COOKIE_DOMAIN = current_domain
            settings.SESSION_COOKIE_DOMAIN = current_domain
