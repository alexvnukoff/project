from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
import datetime
from appl.models import Company, PayPalPayment, AdvOrder
from core.models import Relationship, User
from tpp import settings


def verify_payment_status(request):
    """
        Process IPN form PayPal.
        For debugging on local host use: >ngrok.exe -authtoken IV7A72mC4qsjPl5wCVoa -subdomain=tppcenter 80
    """
    payment = PayPalPayment()
    # for production call: payment.verifyAndSave(request, pay_env=1)
    if payment.verifyAndSave(request):
        #update company's end_date and paid_till-date
        item_number = payment.getItemNumber()
        if len(item_number):
            if 'Company ID:' in item_number:
                #get Company ID from string
                s = [token for token in item_number.split() if token.isdigit()]
                item_id = s[0]
                if len(item_id):
                    # here additional checks: receiver email, sum, currency

                    try:
                        comp = Company.objects.get(pk=int(item_id))
                        new_end_date = comp.paid_till_date + datetime.timedelta(days=365)
                        comp.end_date = new_end_date
                        comp.paid_till_date = new_end_date
                        comp.save()
                    except:
                        return HttpResponse('False')
                else:
                    return HttpResponse('False')
            else:
                return HttpResponse('False')
        else:
            return HttpResponse('False')
    else:
        return HttpResponse('False')


def pay_for_adv(request):
    payment = PayPalPayment()
    # for production call: payment.verifyAndSave(request, pay_env=1)
    if payment.verifyAndSave(request):
        #update company's end_date and paid_till-date
        item_number = payment.getItemNumber()

        if len(item_number):

            try:
                order = AdvOrder.objects.get(pk=item_number)
            except ObjectDoesNotExist:
                return HttpResponse('False')

            orderCost = order.getAttributeValues("COST")[0]

            status = request.POST.get('payment_status')
            receiver = request.POST.get('receiver_email')
            amount = request.POST.get('mc_gross')
            currency = request.POST.get('mc_currency')

            if status == "Completed" and receiver == settings.PAYPAL_RECEIVER_EMAIL and amount == orderCost \
                    and currency == 'USD':

                user = User.objects.filter(is_superuser=True)[0]

                Relationship.setRelRelationship(order, payment, user)

            else:
                return HttpResponse('False')
        else:
            return HttpResponse('False')
    else:
        return HttpResponse('False')