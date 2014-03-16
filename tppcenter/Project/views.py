__author__ = 'user'
from django.shortcuts import render_to_response
from django.template import RequestContext

def project(request, template, section):

    templateParams = {
        'current_section': section,
    }

    return render_to_response("Project/" + template, templateParams, context_instance=RequestContext(request))
