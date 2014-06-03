from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, get_object_or_404
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import urllib.error
import datetime
from appl.models import Company


def verify_payment_status(request):
    """
        Process IPN form PayPal.
        For debugging on local host use: >ngrok.exe -authtoken IV7A72mC4qsjPl5wCVoa -subdomain=tppcenter 80
    """
    if request.method == 'POST':
        # SEND POSTBACK FOR PAYMENT VALIDATION
        # prepares provided data set to inform PayPal we wish to validate the response
        data = request.POST.copy()
        data['cmd'] = "_notify-validate"
        params = urlencode(data).encode('utf-8')
        # sends the data and request to the PayPal
        #req = Request('https://www.paypal.com/cgi-bin/webscr', params)
        req = Request('https://www.sandbox.paypal.com/cgi-bin/webscr', params)
        #reads the response back from PayPal
        response = urlopen(req)
        status = response.read()
        # If not verified
        if not status == b"VERIFIED":
            return False
        #update company's end_date and paid_till-date
        item_number = request.POST.get('item_number', '')
        if len(item_number):
            if 'Company ID:' in item_number:
                #get Company ID from string
                s = [token for token in item_number.split() if token.isdigit()]
                item_id = s[0]
                if len(item_id):
                    try:
                        comp = Company.objects.get(pk=int(item_id))
                        new_end_date = comp.paid_till_date + datetime.timedelta(days=365)
                        comp.end_date = new_end_date
                        comp.paid_till_date = new_end_date
                        comp.save()
                    except:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False

    return True