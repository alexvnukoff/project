from django.shortcuts import render_to_response
from django.template import RequestContext

from centerpokupok.models import B2CProductCategory


def category_list(request):
    categories = B2CProductCategory.objects.filter(level=0).order_by('name').prefetch_related('children')

    return render_to_response("centerpokupok/Categories/index.html",
                              {'categories': categories},
                              context_instance=RequestContext(request))











