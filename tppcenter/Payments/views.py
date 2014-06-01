from django.shortcuts import render_to_response
from django.template import RequestContext


def getPaymentDetails(request):

    payment_details = {}

    templateParams = {
        'payment_details': payment_details
    }

    return render_to_response("Payments/index.html", templateParams, context_instance=RequestContext(request))
