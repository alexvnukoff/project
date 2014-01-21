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

    dictStructured = func.setStructureForHiearhy(hierarchyStructure, categories)
    categotySelect = dictStructured


    flagList = func.getItemsList("Country", "NAME", "FLAG")

    return render_to_response("Categories/index.html", locals())











