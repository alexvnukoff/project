from itertools import count
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from appl.models import *
from core.models import Value, Item, Attribute, Dictionary
from appl import func
from datetime import timedelta, datetime

from django.conf import settings

def set_news_list(request):
    #dict = Dictionary.objects.get(title="Sex")
    id = settings.SITE_ID

@login_required
def cabinet(request):
    if request.user.first_name and request.user.last_name:
        owner = request.user.first_name + ' ' + request.user.last_name
    else:
        owner = request.user.username
    start = datetime.today()
    days=6
    end = start + timedelta(days)
    events = Item.objects.filter(create_date__range=[start, end])
    return render_to_response('appl/cabinet_main.html', {'owner': owner, 'events_array': events, 'period': days},)
