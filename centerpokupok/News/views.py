from django.shortcuts import render
from django.shortcuts import render_to_response
from appl.models import News
from core.models import Value, Item, Attribute, Dictionary
from appl import func

from django.conf import settings

def newsList(request):
    page = request.GET.get('page', 1)
    result = func.getItemsListWithPagination("News", "Name", "Active_From", "Detail_Text", "Photo", page=page)
    newsList = result[0]
    page = result[1]
    if page.number - 2 > 0:
        start = page.number - 2
    else:
        start = 1
    if start + 5 <= page.paginator.num_pages:
        end = start + 5
    else:
        end = page.paginator.num_pages + 1

    paginator_range = range(start, end)

    return render_to_response("News/index.html", locals())


