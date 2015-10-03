from django.conf.urls import patterns, url
from django.contrib import admin

import b24online.Payments.views

admin.autodiscover()


urlpatterns = patterns('',
     url(r'^membership/$', b24online.Payments.views.membership_payment, name="membership_payment"),
     url(r'^product/$', b24online.Payments.views.product_payment, name="product_payment"),
     url(r'^advertisement/$', b24online.Payments.views.pay_for_adv, name="pay_for_adv"),
)