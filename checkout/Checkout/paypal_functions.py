#!/usr/bin/python
'''********************************************
	Module contains calls to PayPal APIs 
	********************************************/'''
from ConfigParser import SafeConfigParser
from urllib import urlencode,quote_plus
import urlparse, urllib
import time
import httplib, ssl, socket
import ssl
ssl.PROTOCOL_SSLv23 = ssl.PROTOCOL_TLSv1
parse_qs = urlparse.parse_qs
parser = SafeConfigParser()
parser.read('paypal_config.ini')

parser.get('Credentials', 'PROXY_HOST')
# Use values from config.php
PROXY_HOST = parser.get('Credentials', 'PROXY_HOST')
PROXY_PORT = parser.get('Credentials', 'PROXY_PORT')
SandboxFlag = parser.get('Credentials', 'SANDBOX_FLAG')

USERACTION_FLAG = parser.get('Credentials','USERACTION_FLAG')


if SandboxFlag=='True':  #API Credentials and URLs for Sandbox		
	API_UserName= parser.get('Credentials', 'PP_USER_SANDBOX')
	API_Password= parser.get('Credentials', 'PP_PASSWORD_SANDBOX')
	API_Signature= parser.get('Credentials', 'PP_SIGNATURE_SANDBOX')
	API_Endpoint = parser.get('Credentials', 'PP_NVP_ENDPOINT_SANDBOX')
	PAYPAL_URL = parser.get('Credentials', 'PP_CHECKOUT_URL_SANDBOX')
		
else:  # API Credentials and URLs for Live		
	API_UserName= parser.get('Credentials', 'PP_USER')
	API_Password= parser.get('Credentials', 'PP_PASSWORD')
	API_Signature= parser.get('Credentials', 'PP_SIGNATURE')
	API_Endpoint = parser.get('Credentials', 'PP_NVP_ENDPOINT_LIVE')
	PAYPAL_URL = parser.get('Credentials', 'PP_CHECKOUT_URL_LIVE')
		
# BN Code 	is only applicable for partners
sBNCode = parser.get('Credentials', 'SBN_CODE')
version= parser.get('Credentials', 'API_VERSION')


'''
* Purpose: 	Prepares the parameters for the SetExpressCheckout API Call.
* Inputs:  
*		parameterArray:     the item details, prices and taxes
*		returnURL:			the page where buyers return to after they are done with the payment review on PayPal
*		cancelURL:			the page where buyers return to when they cancel the payment review on PayPal
*'''
def CallShortcutExpressCheckout( paramsArray, returnURL, cancelURL):		
	#------------------------------------------------------------------------------------------------------------------------------------
	# Construct the parameter string that describes the SetExpressCheckout API call in the shortcut implementation
	# For more information on the customizing the parameters passed refer: https:#developer.paypal.com/docs/classic/express-checkout/integration-guide/ECCustomizing/
			
	#Mandatory parameters for SetExpressCheckout API call
	if paramsArray["PAYMENTREQUEST_0_AMT"] is not None:
		nvpstr = "&PAYMENTREQUEST_0_AMT="+ paramsArray["PAYMENTREQUEST_0_AMT"]
		

	if paramsArray.has_key("paymentType") and paramsArray["paymentType"] is not None:
		nvpstr = nvpstr + "&PAYMENTREQUEST_0_PAYMENTACTION=" +  paramsArray["paymentType"]
			

	if returnURL is not None:
		nvpstr = nvpstr + "&RETURNURL=" + returnURL

	if cancelURL is not None:
		nvpstr = nvpstr + "&CANCELURL=" + cancelURL

	#Optional parameters for SetExpressCheckout API call
	if paramsArray["currencyCodeType"] is not None:  	
		nvpstr = nvpstr + "&PAYMENTREQUEST_0_CURRENCYCODE=" + paramsArray["currencyCodeType"]
	

	if paramsArray["PAYMENTREQUEST_0_ITEMAMT"] is not None:
		nvpstr = nvpstr + "&PAYMENTREQUEST_0_ITEMAMT=" + paramsArray["PAYMENTREQUEST_0_ITEMAMT"]

	if paramsArray["PAYMENTREQUEST_0_TAXAMT"] is not None:
		nvpstr = nvpstr + "&PAYMENTREQUEST_0_TAXAMT=" + paramsArray["PAYMENTREQUEST_0_TAXAMT"]

	if  paramsArray["PAYMENTREQUEST_0_SHIPPINGAMT"] is not None:			
		nvpstr = nvpstr + "&PAYMENTREQUEST_0_SHIPPINGAMT=" + paramsArray["PAYMENTREQUEST_0_SHIPPINGAMT"]
			

	if  paramsArray["PAYMENTREQUEST_0_HANDLINGAMT"] is not None:			
		nvpstr = nvpstr + "&PAYMENTREQUEST_0_HANDLINGAMT=" + paramsArray["PAYMENTREQUEST_0_HANDLINGAMT"]
			

	if  paramsArray["PAYMENTREQUEST_0_SHIPDISCAMT"] is not None:			
		nvpstr = nvpstr + "&PAYMENTREQUEST_0_SHIPDISCAMT=" + paramsArray["PAYMENTREQUEST_0_SHIPDISCAMT"]
			

	if  paramsArray["PAYMENTREQUEST_0_INSURANCEAMT"] is not None:			
		nvpstr = nvpstr + "&PAYMENTREQUEST_0_INSURANCEAMT=" + paramsArray["PAYMENTREQUEST_0_INSURANCEAMT"]
			

	if  paramsArray["L_PAYMENTREQUEST_0_NAME0"]:
		nvpstr = nvpstr + "&L_PAYMENTREQUEST_0_NAME0=" + paramsArray["L_PAYMENTREQUEST_0_NAME0"]

	if  paramsArray["L_PAYMENTREQUEST_0_NUMBER0"] is not None:
		nvpstr = nvpstr + "&L_PAYMENTREQUEST_0_NUMBER0=" + paramsArray["L_PAYMENTREQUEST_0_NUMBER0"]

	if  paramsArray["L_PAYMENTREQUEST_0_DESC0"] is not None:
		nvpstr = nvpstr + "&L_PAYMENTREQUEST_0_DESC0=" + paramsArray["L_PAYMENTREQUEST_0_DESC0"]

	if  paramsArray["L_PAYMENTREQUEST_0_AMT0"] is not None:
		nvpstr = nvpstr + "&L_PAYMENTREQUEST_0_AMT0=" + paramsArray["L_PAYMENTREQUEST_0_AMT0"]

	if  paramsArray["L_PAYMENTREQUEST_0_QTY0"] is not None:
		nvpstr = nvpstr + "&L_PAYMENTREQUEST_0_QTY0=" + paramsArray["L_PAYMENTREQUEST_0_QTY0"]

	if  paramsArray["LOGOIMG"] is not None:
		nvpstr = nvpstr + "&LOGOIMG="+ paramsArray["LOGOIMG"]
			

	'''
	* Make the API call to PayPal
	* If the API call succeded, then redirect the buyer to PayPal to begin to authorize payment.  
	* If an error occured, show the resulting errors
	'''
	resArray=hash_call("SetExpressCheckout", nvpstr)
	ack = resArray.get("ACK")
	if ack[0].upper()=="SUCCESS" or ack[0].upper()=="SUCCESSWITHWARNING":
		token = resArray["TOKEN"][0]
	return resArray
		
		
'''
'-------------------------------------------------------------------------------------------------------------------------------------------
' Purpose: 	Prepares the parameters for the SetExpressCheckout API Call.
' Inputs:  
'		paymentAmount:  	Total value of the shopping cart
'		currencyCodeType: 	Currency code value the PayPal API
'		paymentType: 		paymentType has to be one of the following values: Sale or Order or Authorization
'		returnURL:			the page where buyers return to after they are done with the payment review on PayPal
'		cancelURL:			the page where buyers return to when they cancel the payment review on PayPal
'		shipToName:		the Ship to name entered on the merchant's site
'		shipToStreet:		the Ship to Street entered on the merchant's site
'		shipToCity:			the Ship to City entered on the merchant's site
'		shipToState:		the Ship to State entered on the merchant's site
'		shipToCountryCode:	the Code for Ship to Country entered on the merchant's site
'		shipToZip:			the Ship to ZipCode entered on the merchant's site
'		shipToStreet2:		the Ship to Street2 entered on the merchant's site
'		phoneNum:			the phoneNum  entered on the merchant's site
'--------------------------------------------------------------------------------------------------------------------------------------------	
'''
def CallMarkExpressCheckout( shippingDetail, paramsArray,returnUrl,cancelUrl):
	#-----------------------------------------------------------------------------------------------------------------------------------
	#Construct the parameter string that describes the SetExpressCheckout API call in the shortcut implementation
	#Mandatory parameters for SetExpressCheckout API call
	if paramsArray.get("PAYMENTREQUEST_0_AMT")[0] is not None:
		nvpstr = "&PAYMENTREQUEST_0_AMT="+ paramsArray.get("PAYMENTREQUEST_0_AMT")[0]

	if paramsArray.get("paymentType"):
		nvpstr = nvpstr + "&PAYMENTREQUEST_0_PAYMENTACTION=" +  paramsArray.get("paymentType")[0]

	if returnUrl is not None:
		nvpstr = nvpstr + "&RETURNURL=" + returnUrl

	if cancelUrl is not None:
		nvpstr = nvpstr + "&CANCELURL=" + cancelUrl

	#Optional parameters for SetExpressCheckout API call
	if paramsArray.get("currencyCodeType")[0] is not None:  
		nvpstr = nvpstr + "&PAYMENTREQUEST_0_CURRENCYCODE=" + paramsArray.get("currencyCodeType")[0]

	if paramsArray.get("PAYMENTREQUEST_0_ITEMAMT")[0] is not None:
		nvpstr = nvpstr + "&PAYMENTREQUEST_0_ITEMAMT=" + paramsArray.get("PAYMENTREQUEST_0_ITEMAMT")[0]

	if paramsArray.get("PAYMENTREQUEST_0_TAXAMT")[0] is not None:
		nvpstr = nvpstr + "&PAYMENTREQUEST_0_TAXAMT=" + paramsArray.get("PAYMENTREQUEST_0_TAXAMT")[0]

	if paramsArray.get("PAYMENTREQUEST_0_SHIPPINGAMT")[0] is not None:
		nvpstr = nvpstr + "&PAYMENTREQUEST_0_SHIPPINGAMT=" + paramsArray.get("PAYMENTREQUEST_0_SHIPPINGAMT")[0]

	if paramsArray.get("PAYMENTREQUEST_0_HANDLINGAMT")[0] is not None:
		nvpstr = nvpstr + "&PAYMENTREQUEST_0_HANDLINGAMT=" + paramsArray.get("PAYMENTREQUEST_0_HANDLINGAMT")[0]

	if paramsArray.get("PAYMENTREQUEST_0_SHIPDISCAMT")[0] is not None:
		nvpstr = nvpstr + "&PAYMENTREQUEST_0_SHIPDISCAMT=" + paramsArray.get("PAYMENTREQUEST_0_SHIPDISCAMT")[0]

	if paramsArray.get("PAYMENTREQUEST_0_INSURANCEAMT")[0] is not None:
		nvpstr = nvpstr + "&PAYMENTREQUEST_0_INSURANCEAMT=" + paramsArray.get("PAYMENTREQUEST_0_INSURANCEAMT")[0]

	if paramsArray.get("L_PAYMENTREQUEST_0_NAME0")[0] is not None:
		nvpstr = nvpstr + "&L_PAYMENTREQUEST_0_NAME0=" + paramsArray.get("L_PAYMENTREQUEST_0_NAME0")[0]

	if paramsArray.get("L_PAYMENTREQUEST_0_NUMBER0")[0] is not None:
		nvpstr = nvpstr + "&L_PAYMENTREQUEST_0_NUMBER0=" + paramsArray.get("L_PAYMENTREQUEST_0_NUMBER0")[0]

	if paramsArray.get("L_PAYMENTREQUEST_0_DESC0")[0] is not None:
		nvpstr = nvpstr + "&L_PAYMENTREQUEST_0_DESC0=" + paramsArray.get("L_PAYMENTREQUEST_0_DESC0")[0]

	if paramsArray.get("L_PAYMENTREQUEST_0_AMT0") is not None:
		nvpstr = nvpstr + "&L_PAYMENTREQUEST_0_AMT0=" + paramsArray.get("L_PAYMENTREQUEST_0_AMT0")[0]

	if paramsArray.get("L_PAYMENTREQUEST_0_QTY0") is not None:
		nvpstr = nvpstr + "&L_PAYMENTREQUEST_0_QTY0=" + paramsArray.get("L_PAYMENTREQUEST_0_QTY0")[0]

	if paramsArray.get("LOGOIMG")[0] is not None:
		nvpstr = nvpstr + "&LOGOIMG="+ paramsArray.get("LOGOIMG")[0]
			
		
	nvpstr = nvpstr + "&ADDROVERRIDE=1"
	# Shipping parameters for API call
			
	if shippingDetail["L_PAYMENTREQUEST_FIRSTNAME"] is not None:  
		fullname = shippingDetail.getvalue("L_PAYMENTREQUEST_FIRSTNAME")
		if shippingDetail["L_PAYMENTREQUEST_LASTNAME"] is not None:
			fullname = fullname +"  "+ shippingDetail.getvalue("L_PAYMENTREQUEST_LASTNAME")
			nvpstr = nvpstr + "&PAYMENTREQUEST_0_SHIPTONAME=" + fullname
			
	if shippingDetail["PAYMENTREQUEST_0_SHIPTOSTREET"] is not None:
		nvpstr = nvpstr + "&PAYMENTREQUEST_0_SHIPTOSTREET=" + shippingDetail.getvalue("PAYMENTREQUEST_0_SHIPTOSTREET")
			
	if shippingDetail["PAYMENTREQUEST_0_SHIPTOSTREET2"] is not None:
		nvpstr = nvpstr + "&PAYMENTREQUEST_0_SHIPTOSTREET2=" + shippingDetail.getvalue("PAYMENTREQUEST_0_SHIPTOSTREET2")
			
	if shippingDetail["PAYMENTREQUEST_0_SHIPTOCITY"] is not None:
		nvpstr = nvpstr + "&PAYMENTREQUEST_0_SHIPTOCITY=" + shippingDetail.getvalue("PAYMENTREQUEST_0_SHIPTOCITY")
			
	if shippingDetail["PAYMENTREQUEST_0_SHIPTOSTATE"] is not None:
		nvpstr = nvpstr + "&PAYMENTREQUEST_0_SHIPTOSTATE=" + shippingDetail.getvalue("PAYMENTREQUEST_0_SHIPTOSTATE")

	if shippingDetail["PAYMENTREQUEST_0_SHIPTOZIP"] is not None:
		nvpstr = nvpstr + "&PAYMENTREQUEST_0_SHIPTOZIP=" + shippingDetail.getvalue("PAYMENTREQUEST_0_SHIPTOZIP")

	if shippingDetail["PAYMENTREQUEST_0_SHIPTOCOUNTRY"] is not None:
		nvpstr = nvpstr + "&PAYMENTREQUEST_0_SHIPTOCOUNTRY=" + shippingDetail.getvalue("PAYMENTREQUEST_0_SHIPTOCOUNTRY")


	if "PAYMENTREQUEST_0_SHIPTOPHONENUM" in shippingDetail.keys() and shippingDetail["PAYMENTREQUEST_0_SHIPTOPHONENUM"] is not None:
		nvpstr = nvpstr + "&PAYMENTREQUEST_0_SHIPTOPHONENUM=" + shippingDetail.getvalue("PAYMENTREQUEST_0_SHIPTOPHONENUM")
	nvpstr = nvpstr +"&useraction=commit"
	'''
	* Make the API call to PayPal
	* If the API call succeded, then redirect the buyer to PayPal to begin to authorize payment.  
	* If an error occured, show the resulting errors
	'''
	resArray=hash_call("SetExpressCheckout", nvpstr)	
	ack =resArray["ACK"][0].upper()
	if ack=="SUCCESS" or ack=="SUCCESSWITHWARNING":
		token = resArray["TOKEN"][0]
	return resArray

		
'''Purpose: 	
* Prepares the parameters for the GetExpressCheckoutDetails API Call.
* Inputs:  None
* Returns: The NVP Collection object of the GetExpressCheckoutDetails Call Response.
'''
def GetShippingDetails( token ):		
	'''
	* Build a second API request to PayPal, using the token as the
	*  ID to get the details on the payment authorization
	*'''
	nvpstr="&TOKEN=" + token
	'''/*
	* Make the API call and store the results in an array.  
	* If the call was a success, show the authorization details, and provide an action to complete the payment.  
	* If failed, show the error
	*/'''
	resArray=hash_call("GetExpressCheckoutDetails",nvpstr)
	ack = resArray["ACK"][0].upper()
	return resArray
		

'''
* Purpose: 	Prepares the parameters for the DoExpressCheckoutPayment API Call.
* Inputs:   FinalPaymentAmount:	The total transaction amount.
* Returns: 	The NVP Collection object of the DoExpressCheckoutPayment Call Response.
'''
def ConfirmPayment( FinalPaymentAmt,payer_id,token,currencyCode):		
	''' Gather the information to make the final call to finalize the PayPal payment.  The variable nvpstr
	* holds the name value pairs
	'''
	#mandatory parameters in DoExpressCheckoutPayment call
	if token:
		nvpstr = '&TOKEN=' + urllib.unquote_plus(token)

	if payer_id:
		nvpstr += '&PAYERID=' + urllib.unquote_plus(payer_id)

	nvpstr +='&PAYMENTREQUEST_0_AMT=' + FinalPaymentAmt
	nvpstr +='&PAYMENTREQUEST_0_CURRENCYCODE=' + currencyCode

	''' Make the call to PayPal to finalize payment
	* If an error occured, show the resulting errors
	'''
	resArray=hash_call("DoExpressCheckoutPayment", nvpstr)
	''' Display the API response back to the browser.
	* If the response from PayPal was a success, display the response parameters'
	* If the response was an error, display the errors received using APIError.php.
	'''	
	ack = resArray["ACK"][0]

	return resArray
'''
* hash_call: def to perform the API call to PayPal using API signature
* @methodName is name of API  method.
* @nvpStr is nvp string.
* returns an associtive array containing the response from the server.
'''
def hash_call(methodName,nvpStr):		
	#declaring of global variables
	global API_Endpoint, version , API_UserName, API_Password, API_Signature
	global USE_PROXY, PROXY_HOST, PROXY_PORT
	global gv_ApiErrorURL
	global sBNCode
	#NVPRequest for submitting to server
	nvpreq="METHOD=" + methodName + "&VERSION="+ version + "&PWD=" + API_Password + "&USER=" + API_UserName + "&SIGNATURE=" + API_Signature + nvpStr + "&BUTTONSOURCE=" + sBNCode
	r = urllib.urlopen(API_Endpoint+"?"+nvpreq)
	#getting response from server
	response = r.read()
	nvpResArray = parse_qs(response)
	nvpReqArray=parse_qs(nvpreq)

	return nvpResArray

'''
* Purpose: Redirects to PayPal.com site.
* Inputs:  NVP string.
*  Returns: 
'''
def RedirectToPayPal ( token,mark= False):		
	global PAYPAL_URL
	# Redirect to paypal.com here
	# With useraction=commit user will see "Pay Now" on Paypal website and when user clicks "Pay Now" and returns to our website we can call DoExpressCheckoutPayment API without asking the user
	payPalURL = PAYPAL_URL+ token[0]
	if USERACTION_FLAG == 'True' or  mark :
		payPalURL += '&useraction=commit'

	print "Location:"+ payPalURL +"\r\n"
	exit()


'''
' This def will take NVPString and convert it to an Associative Array and it will decode the response.
' It is usefull to search for a particular key and displaying arrays.
' @nvpstr is NVPString.
' @nvpArray is Associative Array.
'''
def deformatNVP(nvpstr):		
	intial=0
	nvpArray = {}
	while(len(nvpstr)> intial):
		#postion of Key
		keypos= nvpstr.find('=')
		#position of value
		valuepos = nvpstr.find('&') if nvpstr.find('&') >0 else len(nvpstr)
		#getting the Key and Value values and storing in a Associative Array
		keyval=nvpstr[intial:keypos]
		valval=nvpstr[keypos+1:valuepos]
		intial = valuepos
		#decoding the respose
		nvpArray[keyval] = valval
		nvpstr=nvpstr[valuepos+1:]
	
	return nvpArray
