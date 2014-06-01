from django.shortcuts import render_to_response
from django.template import RequestContext


def getPaymentDetails(request):
    """
        Process IPN form PayPal.
        For debugging on local host use: >ngrok.exe -authtoken IV7A72mC4qsjPl5wCVoa -subdomain=tppcenter 80
    """
    payment_details = {}

    templateParams = {
        'payment_details': payment_details
    }

    return render_to_response("Payments/index.html", templateParams, context_instance=RequestContext(request))
