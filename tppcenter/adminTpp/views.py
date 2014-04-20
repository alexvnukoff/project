from appl import func
from django.shortcuts import render_to_response
from django.template import RequestContext

def dashboard(request):

    templateParams = {}
    return render_to_response("adminTpp/index.html", templateParams, context_instance=RequestContext(request))

def users(request):

    ordered = ['email', 'create_date', 'last_login']

    search = request.GET.get('q', None)
    orderField = request.GET.get('field', 'email')
    order = request.GET.get('field', 'email')

    templateParams = {}
    return render_to_response("adminTpp/users.html", templateParams, context_instance=RequestContext(request))