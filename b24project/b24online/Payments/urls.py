from django.conf.urls import url
from paypal.standard.ipn.views import ipn

from appl import func

urlpatterns = [url(r'^companies/$', ipn, {'item_check_callable': func.verify_ipn_request}, name="membership_payment")]