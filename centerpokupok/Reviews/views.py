
from django.shortcuts import render_to_response, get_object_or_404
from appl.models import News, Review
from core.models import Value, Item, Attribute, Dictionary
from appl import func
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist

from django.conf import settings

def reviewList(request):
    page = request.GET.get('page', 1)
    result = func.getItemsListWithPagination("Review", "NAME", "ACTIVE_FROM", "DETAIL_TEXT", "IMAGE", page=page)
    reviewList = result[0]
    page = result[1]
    paginator_range = func.getPaginatorRange(page)

    user = request.user
    return render_to_response("Reviews/index.html", locals())


def reviewDetail(request, item_id):
    review = get_object_or_404(Review, pk=item_id)


    reviewAttr = review.getAttributeValues("NAME", "ACTIVE_FROM", "DETAIL_TEXT", "IMAGE")

    user = request.user


    return render_to_response("Reviews/detail.html", locals())


