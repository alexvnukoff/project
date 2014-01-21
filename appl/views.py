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

@login_required
def cabinet(request):
    if request.user.first_name and request.user.last_name:
        owner = request.user.first_name + ' ' + request.user.last_name
    else:
        owner = request.user.username
    return render_to_response('appl/cabinet_main.html', {'owner': owner,})
