from django.conf.urls import patterns, url
from django.contrib import admin
from paypal.standard.ipn.views import ipn

from appl import func

admin.autodiscover()


urlpatterns = patterns('',
     url(r'^companies/$', ipn, {'item_check_callable': func.verify_ipn_request}, name="membership_payment"),
)