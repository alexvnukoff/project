"""
Cross Site Request Forgery Middleware.

This module provides a middleware that implements protection
against request forgeries from other sites.
"""
from django.conf import settings


class ChangeCsrfCookieDomainMiddleware:


     def process_request(self, request):
          host = request.get_host().split(':')[0]

          if host[:4] == "www":
            host = host[4:]

          if len(host.split(".")) > 2:
             host = host.split(".")
             host = "." + host[1] + "." + host[2]
          else:
              host = "." + host
          allowed = settings.ALLOWED_HOSTS
          if host in allowed:
             settings.CSRF_COOKIE_DOMAIN = host






