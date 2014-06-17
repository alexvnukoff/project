from django.conf.urls import patterns, url
import tppcenter.Payments.views

import tppcenter.views


from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
     url(r'^membership/$', tppcenter.Payments.views.membership_payment, name="membership_payment"),
     url(r'^product/$', tppcenter.Payments.views.product_payment, name="product_payment"),
     url(r'^advertisement/$', tppcenter.Payments.views.pay_for_adv, name="pay_for_adv"),
)