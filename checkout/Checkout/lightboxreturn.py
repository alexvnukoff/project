#!/usr/bin/env python
import socket
import cgi,cgitb,urllib

form = cgi.FieldStorage()

token = ""
payerId = ""

if form.getvalue('token'):
	token = urllib.quote_plus(form.getvalue('token'))
if form.getvalue('PayerID'):
	payerId = urllib.quote_plus(form.getvalue('PayerID'))

url = 'http://'+ socket.gethostbyname(socket.gethostname()) + '/cgi-bin/Checkout/review.py?token='+ token + '&PayerID='+ payerId

print "Content-Type: text/html;charset=utf-8\n\n"
print "<!DOCTYPE html>"

print """\
<html>
  <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>PayPal Demo Portal</title>
      <!--Including Bootstrap style files-->
      <link href="css/bootstrap.min.css" rel="stylesheet">
      <link href="css/bootstrap-responsive.min.css" rel="stylesheet">
  </head>
  <body>
      <div class="container-fluid">
      <div class="row-fluid">
      <div class="span4">
      </div>
      <div class="span5">
<div class="row text-center"><h3>Loading...</h3></div>
<script type="text/javascript">
if (window!=top){top.location.href='%s';} //lightbox return
else
window.location.href='%s';  //return from full page paypal flow
</script>
</body>
</html>""" % (url, url)
