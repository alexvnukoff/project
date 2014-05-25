from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from appl.models import staticPages


def project(request, template, section):

    templateParams = {
        'current_section': section,
    }

    return render_to_response("Project/" + template, templateParams, context_instance=RequestContext(request))

def showPage(request, item_id=None, slug=None):

    page = get_object_or_404(staticPages, pk=item_id)

    attr = page.getAttributeValues('NAME', 'DETAIL_TEXT')

    return render_to_response("Project/detail.html", {'page': attr}, context_instance=RequestContext(request))
