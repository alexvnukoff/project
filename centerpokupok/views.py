from django.shortcuts import render
from django.shortcuts import render_to_response
from appl.models import News, Category, Country, Product
from core.models import Value, Item, Attribute, Dictionary
from appl import func

from django.conf import settings

def home(request):

    newsList = func.getItemsList("News", "Name", "Active_From", "Photo", qty=3)
    hierarchyStructure = Category.hierarchy.getTree(10)
    categories_id = [cat['ID'] for cat in hierarchyStructure]
    categories = Item.getItemsAttributesValues(("NAME",), categories_id)

    sortedHierarchyStructure = _sortMenu(hierarchyStructure)



    level = 0
    for node in sortedHierarchyStructure:
        node['pre_level'] = level
        node['item'] = categories[node['ID']]
        node['parent_item'] = categories[node['PARENT_ID']] if node['PARENT_ID'] is not None else ""
        level = node['LEVEL']


    flagList = func.getItemsList("Country", "NAME", "Flag")



    return render_to_response("index.html", locals())



def about(request):

    return render_to_response("About/About.html")

def set_news_list(request):
    page = request.GET.get('page', 1)
    result = func.getItemsListWithPagination("News", "Anons", "Text", "Image", page=page)

    itemsList = result[0]
    page = result[1]
    return render_to_response('NewsList.html', locals())


def _sortMenu(hierarchyStructure):
    sortedHierarchyStructure = []
    dictToSort = []
    id = hierarchyStructure[0]['ID']
    for i in range(0, len(hierarchyStructure)):
        if hierarchyStructure[i]["LEVEL"] == 1 and hierarchyStructure[i]['ID'] != id:
            id = hierarchyStructure[i]['ID']
            sortedHierarchyStructure.extend(_sortList(dictToSort))
            dictToSort = []

        dictToSort.append(hierarchyStructure[i])

    if len(dictToSort) > 0:
       sortedHierarchyStructure.extend(_sortList(dictToSort))

    return sortedHierarchyStructure

def _sortList(dict):
    sortedDict = []
    i = 0
    while i < len(dict):
        if dict[i]['LEVEL'] > 3:
            dict.pop(i)
            i-= 1
        if dict[i]['ISLEAF'] == 1 and dict[i]["LEVEL"] == 2:
            sortedDict.append(dict.pop(i))
            i -= 1
        i+=1

    dict.extend(sortedDict)
    return dict


