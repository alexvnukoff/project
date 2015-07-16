#!/usr/bin/env python
from paypal_functions import *
import cgi,cgitb
from ConfigParser import SafeConfigParser

form = cgi.FieldStorage()
parser = SafeConfigParser()
parser.read('paypal_config.ini')
USERACTION_FLAG = parser.get('Credentials','USERACTION_FLAG')
	
# Check to see if the Request object contains a variable named 'token'	or Session object contains a variable named TOKEN 
token = ""
if form.getvalue('token'):
	token = form.getvalue('token')

finalPaymentAmount = 0

# If the Request object contains the variable 'token' then it means that the user is coming from PayPal site.	
if  token != "":
	'''/*
	* Calls the GetExpressCheckoutDetails API call
	*'''
	resArrayGetExpressCheckout = GetShippingDetails( token )
	ackGetExpressCheckout = resArrayGetExpressCheckout["ACK"][0].upper()
	if ackGetExpressCheckout == "SUCCESS" or ackGetExpressCheckout == "SUCESSWITHWARNING":		
		'''/*
		* The information that is returned by the GetExpressCheckoutDetails call should be integrated by the partner into his Order Review 
		* page		
		*/'''
		email 				= resArrayGetExpressCheckout["EMAIL"][0] # ' Email address of payer.
		payerId 			= resArrayGetExpressCheckout["PAYERID"][0] # ' Unique PayPal customer account identification number.
		payerStatus		= resArrayGetExpressCheckout["PAYERSTATUS"][0] # ' Status of payer. Character length and limitations: 10 single-byte alphabetic characters.
		firstName			= resArrayGetExpressCheckout["FIRSTNAME"][0] # ' Payer's first name.
		lastName			= resArrayGetExpressCheckout["LASTNAME"][0] # ' Payer's last name.
		cntryCode			= resArrayGetExpressCheckout["COUNTRYCODE"][0] # ' Payer's country of residence in the form of ISO standard 3166 two-character country codes.
		shipToName			= resArrayGetExpressCheckout["PAYMENTREQUEST_0_SHIPTONAME"][0] # ' Person's name associated with this address.
		shipToStreet		= resArrayGetExpressCheckout["PAYMENTREQUEST_0_SHIPTOSTREET"][0] # ' First street address.
		shipToCity			= resArrayGetExpressCheckout["PAYMENTREQUEST_0_SHIPTOCITY"][0] # ' Name of city.
		shipToState		= resArrayGetExpressCheckout["PAYMENTREQUEST_0_SHIPTOSTATE"][0] # ' State or province
		shipToCntryCode	= resArrayGetExpressCheckout["PAYMENTREQUEST_0_SHIPTOCOUNTRYCODE"][0] # ' Country code. 
		shipToZip			= resArrayGetExpressCheckout["PAYMENTREQUEST_0_SHIPTOZIP"][0] # ' U.S. Zip code or other country-specific postal code.
		addressStatus 		= resArrayGetExpressCheckout["ADDRESSSTATUS"][0] # ' Status of street address on file with PayPal 
		totalAmt   		= resArrayGetExpressCheckout["PAYMENTREQUEST_0_AMT"][0] # ' Total Amount to be paid by buyer
		currencyCode       = resArrayGetExpressCheckout["CURRENCYCODE"][0] # 'Currency being used 
		shippingAmt        = resArrayGetExpressCheckout["PAYMENTREQUEST_0_SHIPPINGAMT"][0] # 'Shipping amount 
		finalPaymentAmount = totalAmt
		'''/*
		* Add check here to verify if the payment amount stored in session is the same as the one returned from GetExpressCheckoutDetails API call
		* Checks whether the session has been compromised
		*/'''
		 
	else:
		#Display a user friendly Error on the page using any of the following error information returned by PayPal
		ErrorCode = resArrayGetExpressCheckout["L_ERRORCODE0"][0]
		ErrorShortMsg = resArrayGetExpressCheckout["L_SHORTMESSAGE0"][0]
		ErrorLongMsg = resArrayGetExpressCheckout["L_LONGMESSAGE0"][0]
		ErrorSeverityCode = resArrayGetExpressCheckout["L_SEVERITYCODE0"][0]
		print "Content-Type:text/html\n\n"
		print "GetExpressCheckoutDetails API call failed. "
		print "Detailed Error Message: " + ErrorLongMsg
		print "Short Error Message: " + ErrorShortMsg
		print "Error Code: " + ErrorCode
		print "Error Severity Code: " + ErrorSeverityCode
			
#/* Review block start */	
if USERACTION_FLAG=='False' and form.getvalue('shipping_method'):
	if form.getvalue('shipping_method'):
		new_shipping = form.getvalue('shipping_method') #need to change this value, just for testing
		if new_shipping=="":
			new_shipping =shippingAmt	
	if shippingAmt > 0:
		finalPaymentAmount = float(totalAmt) + float(new_shipping) - float(shippingAmt)
'''/* Review block end */
/*
* Calls the DoExpressCheckoutPayment API call
*/'''
resArrayDoExpressCheckout = ConfirmPayment ( str(finalPaymentAmount),form.getvalue('PayerID'),token,currencyCode )
ackDoExpressCheckout =resArrayDoExpressCheckout.get("ACK")[0].upper()
import header
if ackDoExpressCheckout == "SUCCESS" or ackDoExpressCheckout == "SUCCESSWITHWARNING":
	transactionId		= resArrayDoExpressCheckout["PAYMENTINFO_0_TRANSACTIONID"][0] # ' Unique transaction ID of the payment. Note:  If the PaymentAction of the request was Authorization or Order, this value is your AuthorizationID for use with the Authorization & Capture APIs. 
	transactionType 	= resArrayDoExpressCheckout["PAYMENTINFO_0_TRANSACTIONTYPE"][0] #' The type of transaction Possible values: l  cart l  express-checkout 
	paymentType		= resArrayDoExpressCheckout["PAYMENTINFO_0_PAYMENTTYPE"][0]  #' Indicates whether the payment is instant or delayed. Possible values: l  none l  echeck l  instant 
	orderTime 			= resArrayDoExpressCheckout["PAYMENTINFO_0_ORDERTIME"][0]  #' Time/date stamp of payment
	amt				= resArrayDoExpressCheckout["PAYMENTINFO_0_AMT"][0]  #' The final amount charged, including any shipping and taxes from your Merchant Profile.
	currencyCode		= resArrayDoExpressCheckout["PAYMENTINFO_0_CURRENCYCODE"][0]  #' A three-character currency code for one of the currencies listed in PayPay-Supported Transactional Currencies. Default: USD. 
	'''/*
	* Status of the payment: 
	* Completed: The payment has been completed, and the funds have been added successfully to your account balance.
	* Pending: The payment is pending. See the PendingReason element for more information. 
	*/'''
	paymentStatus	= resArrayDoExpressCheckout["PAYMENTINFO_0_PAYMENTSTATUS"][0]
	'''/*
	* The reason the payment is pending 
	*/'''
	pendingReason	= resArrayDoExpressCheckout["PAYMENTINFO_0_PENDINGREASON"][0]
	'''/*
	* The reason for a reversal if TransactionType is reversal 
	*/'''
	reasonCode		= resArrayDoExpressCheckout["PAYMENTINFO_0_REASONCODE"][0] 
	htmlcode ="""\
		<span class="span4">
    		</span>
    		<span class="span5">
    			<div class="hero-unit">
    			<!-- Display the Transaction Details-->
    			<h4> {firstName} 
    				{lastName}  , Thank you for your Order </h4>
    			
    			<h4> Shipping Details: </h4>
				{shipToName} <br>
				{shipToStreet} <br>
				{shipToCity} <br>
				{shipToState} - {shipToZip} </p>
    			<p>Transaction ID:  {transactionId} </p>
    			<p>Transaction Type:{transactionType} </p>
    			<p>Payment Total Amount:  {amt} </p>
    			<p>Currency Code:  {currencyCode} </p>
    			<p>Payment Status:  {paymentStatus} </p>
    			<p>Payment Type:  {paymentType} </p>
    			<h3> Click <a href='index.py'>here </a> to return to Home Page</h3>
    			</div>
    		</span>
    		<span class="span3">
    		</span>"""
	print htmlcode.format(firstName=firstName,lastName=lastName,shipToName=shipToName,shipToStreet=shipToStreet,shipToCity=shipToCity,shipToState=shipToState,shipToZip=shipToZip,transactionId=transactionId,transactionType=transactionType,amt=amt,currencyCode=currencyCode,paymentStatus=paymentStatus,paymentType=paymentType)
	
else: 
	#Display a user friendly Error on the page using any of the following error information returned by PayPal
	ErrorCode = resArrayDoExpressCheckout["L_ERRORCODE0"][0]
	ErrorShortMsg = resArrayDoExpressCheckout["L_SHORTMESSAGE0"][0]
	ErrorLongMsg = resArrayDoExpressCheckout["L_LONGMESSAGE0"][0]
	ErrorSeverityCode = resArrayDoExpressCheckout["L_SEVERITYCODE0"][0]
	if ErrorCode == 10486:  #Transaction could not be completed error because of Funding failure. Should redirect user to PayPal to manage their funds.
		'''<!--<div class="hero-unit">
		Display the Transaction Details
    		<h4> There is a Funding Failure in your account. You can modify your funding sources to fix it and make purchase later. </h4>
    		Payment Status:-->'''
    		#print(resArrayDoExpressCheckout["PAYMENTINFO_0_PAYMENTSTATUS"])
		RedirectToPayPal ( resArray["TOKEN"] )
    		print """<!--<h3> Click <a href='https:#www.sandbox.paypal.com/'>here </a> to go to PayPal site.</h3> <!--Change to live PayPal site for production--><!--</div>-->"""
			
	else:
		print "DoExpressCheckout API call failed. "
		print "Detailed Error Message: " + ErrorLongMsg
		print "Short Error Message: " + ErrorShortMsg
		print "Error Code: " + ErrorCode
		print "Error Severity Code: " + ErrorSeverityCode
		
import footer
