from django.conf.urls import patterns, url
import tppcenter.Payments.views

import tppcenter.views


from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
     url(r'^$', tppcenter.Payments.views.getPaymentDetails, name="payment_details"),
     #(?P<company>[0-9]+)
)