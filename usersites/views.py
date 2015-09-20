from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _


def get_wall(request):
    current_section = _("Wall")
    title = _("Wall")

    template_params = {
        'current_section': current_section,
        'title': title
    }

    return render_to_response("contentPage.html", template_params, context_instance=RequestContext(request))