#!/usr/bin/env python
import socket
print "Content-Type: text/html;charset=utf-8\n\n"
print "<!DOCTYPE html>"
print """\
<html>
  <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>PayPal Demo Portal</title>
      <!--Including Bootstrap style files-->
      <link href="http://%s/css/bootstrap.min.css" rel="stylesheet">
      <link href="http://%s/css/bootstrap-responsive.min.css" rel="stylesheet">
  </head>
  <body>
      <div class="container-fluid">
      <div class="well">
         <h2 class="text-center"><img src="http://%s/img/logo.jpg">Checkout with PayPal Demo</h2>
      </div>
      <div class="row-fluid">""" %(socket.gethostbyname(socket.gethostname()),socket.gethostbyname(socket.gethostname()),socket.gethostbyname(socket.gethostname()))
