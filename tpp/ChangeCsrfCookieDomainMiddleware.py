"""
Change cookie domain to accept form sub domains( Lang sub domains )
"""
from django.conf import settings


class ChangeCsrfCookieDomainMiddleware:


    def process_request(self, request):

        current_domain = request.get_host().split('.')

        if current_domain[0] == "www":
            current_domain.pop()

        if len(current_domain) > 2:
            current_domain = [""] + [current_domain[-2]] + [current_domain[-1]]
        else:
            current_domain = [""] + current_domain


        current_domain = ".".join(current_domain)

        allowed = settings.ALLOWED_HOSTS

        if current_domain in allowed or "*" in allowed:
            settings.CSRF_COOKIE_DOMAIN = current_domain
            settings.SESSION_COOKIE_DOMAIN = current_domain
