#!/usr/bin/env python
from paypal_functions import *
import cgi
import cgitb; cgitb.enable()
from ConfigParser import SafeConfigParser
import urllib,urlparse
import socket

'''------------------------------------
' Calls the SetExpressCheckout API call
'
' The CallMarkExpressCheckout function is defined in the file paypal_functions.php,
' it is included at the top of this file.'''
#print "Content-Type:text/html\n\n"
#print _SESSION
form = cgi.FieldStorage()
itemDetail = parse_qs(form.getvalue("form_fields"))
parser = SafeConfigParser()
parser.read('paypal_config.ini')
USERACTION_FLAG = parser.get('Credentials','USERACTION_FLAG')
if USERACTION_FLAG == 'True':
        returnURL = 'http://'+socket.gethostbyname(socket.gethostname())+ '/cgi-bin/Checkout/return.py'
else:
        returnURL = 'http://'+socket.gethostbyname(socket.gethostname())+ '/cgi-bin/Checkout/review.py'
cancelURL = 'http://'+socket.gethostbyname(socket.gethostname())+ '/cgi-bin/Checkout/cancel.py'
returnMarkURL = 'http://'+socket.gethostbyname(socket.gethostname())+ '/cgi-bin/Checkout/return.py'
shippingDetail = form
paymentAmount = itemDetail.get('PAYMENTREQUEST_0_AMT')[0]
if form.getvalue("shipping_method"):
	new_shipping = form.getvalue("shipping_method")
	if itemDetail.get('PAYMENTREQUEST_0_SHIPPINGAMT')[0] > 0 :
		paymentAmount = float(paymentAmount) + float(new_shipping) - float(itemDetail.get('PAYMENTREQUEST_0_SHIPPINGAMT')[0])
		itemDetail['PAYMENTREQUEST_0_SHIPPINGAMT'] = [ new_shipping ]
		itemDetail['PAYMENTREQUEST_0_AMT'] = [ str(paymentAmount)]
	
#Call SetExpressCheckout for mark
resArray = CallMarkExpressCheckout (shippingDetail, itemDetail,returnMarkURL,cancelURL)

ack = resArray["ACK"][0].upper()
if ack== "SUCCESS" or ack == "SUCCESSWITHWARNING" : #Check if the API is SUCCESS, Process if it is SUCCESS
	RedirectToPayPal(resArray["TOKEN"],True)
else:
	#Display a user friendly Error on the page using any of the following error information returned by PayPal
	ErrorCode = resArray["L_ERRORCODE0"][0]
	ErrorShortMsg = resArray["L_SHORTMESSAGE0"][0]
	ErrorLongMsg = resArray["L_LONGMESSAGE0"][0]
	ErrorSeverityCode = resArray["L_SEVERITYCODE0"][0]
	print "Content-Type:text/html\n\n"
	print "SetExpressCheckout API call failed "
	print "Detailed Error Message: " + ErrorLongMsg
	print "Short Error Message: " + ErrorShortMsg
	print "Error Code: " + ErrorCode
	print "Error Severity Code: " + ErrorSeverityCode

