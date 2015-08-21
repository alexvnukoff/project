from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from b24online.models import StaticPage


def project(request, template, section):
    template_params = {
        'current_section': section,
    }

    return render_to_response("Project/" + template, template_params, context_instance=RequestContext(request))


def show_page(request, item_id=None, slug=None):
    page = get_object_or_404(StaticPage, pk=item_id)

    return render_to_response("Project/detail.html", {'page': page}, context_instance=RequestContext(request))
