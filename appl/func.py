from django.db import models
from core.models import Item
from appl.models import News


def getItemsList(cls,  *attr, qty=None):
    items = eval(cls).objects.select_related().all()[:qty]
    itemsList = {}
    for item in items:
        itemsList[item.name] = item.getAttributesValue(*attr)
    return itemsList

