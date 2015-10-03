"""
WSGI config for tpp project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
import sys

from django.core.handlers.wsgi import WSGIHandler

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tpp.usersites_settings")
os.environ['DJANGO_SETTINGS_MODULE'] = "tpp.usersites_settings"

application = WSGIHandler()
