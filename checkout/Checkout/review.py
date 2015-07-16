#!/usr/bin/env python
import cgi,cgitb,urllib
import paypal_functions
from paypal_functions import *
from ConfigParser import SafeConfigParser

#Read Config File
parser = SafeConfigParser()
parser.read('paypal_config.ini')
USERACTION_FLAG = parser.get('Credentials','USERACTION_FLAG')


form = cgi.FieldStorage()
token = ""
if form.getvalue('token'):
	token = form.getvalue('token')

if token != "" and USERACTION_FLAG != 'True':
	'''Calls the GetExpressCheckoutDetails API call'''
	resArrayGetExpressCheckout = GetShippingDetails( token )
	ackGetExpressCheckout = resArrayGetExpressCheckout["ACK"][0].upper()
	if ackGetExpressCheckout == "SUCCESS" or ackGetExpressCheckout == "SUCESSWITHWARNING":
		'''
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
		shippingAmt        = resArrayGetExpressCheckout["PAYMENTREQUEST_0_SHIPPINGAMT"][0] # 'Currency being used 
		'''
		* Add check here to verify if the payment amount stored in session is the same as the one returned from GetExpressCheckoutDetails API call
		* Checks whether the session has been compromised
		/'''
	else:
		#Display a user friendly Error on the page using any of the following error information returned by PayPal
		ErrorCode =  resArrayGetExpressCheckout["L_ERRORCODE0"][0]
		ErrorShortMsg = resArrayGetExpressCheckout["L_SHORTMESSAGE0"][0]
		ErrorLongMsg = resArrayGetExpressCheckout["L_LONGMESSAGE0"][0]
		ErrorSeverityCode = resArrayGetExpressCheckout["L_SEVERITYCODE0"][0]
		print "Content-Type:text/html\n\n"
		print "GetExpressCheckoutDetails API call failed. "
		print "Detailed Error Message: " + ErrorLongMsg
		print "Short Error Message: " +ErrorShortMsg
		print "Error Code: " + ErrorCode
		print "Error Severity Code: " + ErrorSeverityCode


		
import header
func ="""{
					var e = document.getElementById("shipping_method");
					var shipAmt = e.options[e.selectedIndex].value;
					if (shipAmt =="")
						shipAmt = oldshipAmt;
					var newAmt = parseInt(shipAmt)+origAmt-oldshipAmt;					
					document.getElementById("amount").innerHTML=newAmt;
				}"""
htmlcode = """\
	<div class="span4">
	</div>
	<div class="span5">
	<table>
		<tbody>
			<tr><td><h4>Shipping Address</h5></td><td><h4>Billing Address</h4></td></tr>
			<tr><td> {shipToName}		</td><td>{shipToName}		</td></tr>
			<tr><td> {shipToStreet}	</td><td> {shipToStreet}	</td></tr>
			<tr><td>	{shipToCity}		</td><td>{shipToCity}	</td></tr>
			<tr><td>{shipToState}	</td><td>{shipToState}		</td></tr>
			<tr><td>{shipToCntryCode} </td><td>{shipToCntryCode}	</td></tr>
			<tr><td>{shipToZip}		</td><td>{shipToZip}		</td></tr>
			<tr><td colspan="2">&nbsp</td></tr>
			<tr><td colspan="2">&nbsp</td></tr>
			<tr><td>Total Amount:</td><td id='amount'>{totalAmt}   		</td></tr>
	
			<tr><td>Currency Code:</td><td>{currencyCode}   	</td></tr>
			<tr><td>&nbsp;</td></tr>
			<script>
			var origAmt={totalAmt};
			var oldshipAmt={shippingAmt};
			function updateAmount(){javascript}			
			</script>		
			<tr><td><h3>Shipping Method</h3></td></tr>
				<form action="return.py" name="order_confirm" method="POST">
					<tr><td>Shipping methods: </td><td><select name="shipping_method" id="shipping_method" style="width: 250px;" class="required-entry" onChange="updateAmount();">
						<option value="">Please select a shipping method...</option>		
						<optgroup label="United Parcel Service" style="font-style:normal;">
						<option value="2.00">
						Worldwide Expedited - $2.00</option>
						<option value="3.00">
						Worldwide Express Saver - $3.00</option>
						</optgroup>
						<optgroup label="Flat Rate" style="font-style:normal;">
						<option value="0.00">
						Fixed - $0.00</option>
						</optgroup>
						</select><br></td></tr>
					<tr><td><input type="Submit" name="confirm" alt="Check out with PayPal" class="btn btn-primary btn-large" value="Confirm Order"></td></tr>
			<input type="hidden" name="token" value={token}></input>			
			<input type="hidden" name="PayerID" value={payerID}></input>
				</form>
			</tbody>
		</table>
	</div>
	<div class="span3">
	</div>
         """
print htmlcode.format(shipToName=shipToName,shipToStreet=shipToStreet,shipToCity=shipToCity,shipToState=shipToState,shipToCntryCode=shipToCntryCode,shipToZip=shipToZip,totalAmt=totalAmt,currencyCode=currencyCode,token=form.getvalue('token'),payerID=urllib.quote_plus(form.getvalue('PayerID')),shippingAmt=shippingAmt,javascript=func)
import footer
