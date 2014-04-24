from django.shortcuts import render
from django.shortcuts import render_to_response
from appl.models import News
from django.contrib.sites.models import get_current_site
from core.models import Value, Item, Attribute, Dictionary

from django.conf import settings

def home(request):
    current_site = get_current_site(request)
    sitename = current_site.domain
    return render_to_response("index.html")

