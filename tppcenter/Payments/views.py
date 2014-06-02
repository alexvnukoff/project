from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

def getPaymentDetails(request):
    """
        Process IPN form PayPal.
        For debugging on local host use: >ngrok.exe -authtoken IV7A72mC4qsjPl5wCVoa -subdomain=tppcenter 80
    """
    payment_details = {}
    item_number = request.POST.get('item_number', '')
    if len(item_number):
        payment_details['ITEM_ID'] = item_number

    payment_details['ITEM_NAME'] = request.POST.get('item_name', '')
    '''
    templateParams = {
        'payment_details': payment_details
    }

    return render_to_response("Payments/index.html", templateParams, context_instance=RequestContext(request))
    '''
    return HttpResponse('Membership of your Company is paid successfully!')
    #http://127.0.0.1/companies/bbb-862.html