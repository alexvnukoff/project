from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
import datetime
from dateutil.parser import parse
from appl.models import Company, PayPalPayment, AdvOrder, Product
from core.models import Relationship, User
from tpp import settings


def membership_payment(request):
    """
        Process IPN from PayPal for membership payments.
        For debugging on local host use: >ngrok.exe -authtoken IV7A72mC4qsjPl5wCVoa -subdomain=tppcenter 80
    """
    payment = PayPalPayment()
    # for production call: payment.verifyAndSave(request, pay_env=1)
    if payment.verifyAndSave(request, pay_env=0):
        if payment.getPaymentStatus() == 'Completed':
            #update company's end_date and paid_till-date
            item_number = payment.getItemNumber()
            if len(item_number):
                if 'Company ID:' in item_number:
                    #get Company ID from string
                    s = [token for token in item_number.split() if token.isdigit()]
                    item_id = s[0]
                    if len(item_id):
                        # here additional checks: receiver email, sum, currency
                        receiver = payment.getPaymentReceiver_s()
                        amount = payment.getPaymentAmount()
                        currency = payment.getPaymentCurrency()

                        if receiver == settings.PAYPAL_RECEIVER_EMAIL and float(amount) == 100.0 and currency == 'USD':
                            try:
                                comp = Company.objects.get(pk=int(item_id))
                                new_end_date = comp.paid_till_date + datetime.timedelta(days=365)
                                comp.end_date = new_end_date
                                comp.paid_till_date = new_end_date
                                comp.save()
                            except:
                                return HttpResponse('False')

                            if User.objects.filter(email=receiver).exists():
                                user = User.objects.get(email=receiver)
                            else:
                                try:
                                    rel = Relationship.objects.filter(parent__c2p__parent__c2p__parent=comp.pk, type='relation', is_admin=True)[0]
                                    user = User.objects.get(id=rel.child.id)
                                except:
                                    user = User.objects.filter(is_superuser=True)[0]

                            Relationship.setRelRelationship(comp, payment, user)
                        else:
                            return HttpResponse('False')
                    else:
                        return HttpResponse('False')
                else:
                    return HttpResponse('False')
            else:
                return HttpResponse('False')
        else:
            return HttpResponse('False')
    else:
        return HttpResponse('False')

    return HttpResponse()


def product_payment(request):
    """
        Process IPN from PayPal for Product payments.
        For debugging on local host use: >ngrok.exe -authtoken IV7A72mC4qsjPl5wCVoa -subdomain=tppcenter 80
    """
    payment = PayPalPayment()
    # for production call: payment.verifyAndSave(request, pay_env=1)
    if payment.verifyAndSave(request, pay_env=0):
        if payment.getPaymentStatus() == 'Completed':
            #create relationship between Product and payment transaction
            item_number = payment.getItemNumber()
            if len(item_number):
                if 'Company:' in item_number:
                    #get Product ID from string
                    s = [token for token in item_number.split() if token.isdigit()]
                    item_id = s[0]
                    if len(item_id):
                        # here additional checks: receiver email, sum, currency
                        receiver = payment.getPaymentReceiver_s()
                        amount = payment.getPaymentAmount()
                        qty = payment.getItemQty()
                        currency = payment.getPaymentCurrency()

                        if receiver == settings.PAYPAL_RECEIVER_EMAIL:
                            try:
                                prod = Product.objects.get(pk=int(item_id))
                                data = prod.getAttributeValues('COST','CURRENCY')
                            except:
                                return HttpResponse('False')

                            if User.objects.filter(email=receiver).exists():
                                user = User.objects.get(email=receiver)
                            else:
                                user = User.objects.filter(is_superuser=True)[0]

                            a1 = float(data.get('COST', '')[0])
                            a2 = data.get('CURRENCY', '')[0]
                            if a1*float(qty) == float(amount) and a2 == currency:
                                Relationship.setRelRelationship(prod, payment, user)
                            else:
                                return HttpResponse('False')
                        else:
                            return HttpResponse('False')
                    else:
                        return HttpResponse('False')
                else:
                    return HttpResponse('False')
            else:
                return HttpResponse('False')
        else:
            return HttpResponse('False')
    else:
        return HttpResponse('False')

    return HttpResponse()


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
                end_date = order.getAttributeValues('END_EVENT_DATE')
                order.end_date = parse(end_date[0])
                order.save()
                return HttpResponse('')
            else:
                return HttpResponse('False')
        else:
            return HttpResponse('False')
    else:
        return HttpResponse('False')
