from django.shortcuts import render
from django.shortcuts import render_to_response
from appl.models import News, Category
from core.models import Value, Item, Attribute, Dictionary
from appl import func
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist

from django.conf import settings

def categoryList(request):
    hierarchyStructure = Category.hierarchy.getTree(10)
    categories_id = [cat['ID'] for cat in hierarchyStructure]
    categories = Item.getItemsAttributesValues(("NAME",), categories_id)
    level = 0
    letter = ""
    dictStructured = {}
    for node in hierarchyStructure:
        if node['LEVEL'] == 1:
            i = categories[node['ID']]['NAME'][0]
            nameOfList = categories[node['ID']]['NAME'][0]
            dictStructured[nameOfList] = {}
            node['item'] = categories[node['ID']]
            dictStructured[nameOfList]['Parent'] = node




        else:
            node['pre_level'] = level
            node['item'] = categories[node['ID']]
            node['parent_item'] = categories[node['PARENT_ID']] if node['PARENT_ID'] is not None else ""
            level = node['LEVEL']
            dictStructured[nameOfList][categories[node['ID']]['NAME'][0]] = node




    flagList = func.getItemsList("Country", "NAME", "Flag")

    return render_to_response("Categories/index.html", locals())











