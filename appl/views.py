from itertools import count
from django.shortcuts import render_to_response
from appl.models import *
from core.models import Value, Item, Attribute, Dictionary
from appl import func

from django.conf import settings

def set_news_list(request):
    #dict = Dictionary.objects.get(title="Sex")
    #dict.deleteSlot("Jopa")
    id = settings.SITE_ID

