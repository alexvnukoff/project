from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.timezone import now
from registration.backends.default.views import RegistrationView
from registration.forms import RegistrationFormUniqueEmail
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _

from appl.models import Cabinet
from appl import func
from centerpokupok.models import B2CProduct


def home(request, country=None):
    products = B2CProduct.get_active_objects().order_by('-created_at')[:4]
    top_product_list = B2CProduct.get_active_objects().order_by('?')[:4]
    coupons = B2CProduct.get_active_objects().filter(coupon_dates__contains=now().date(), coupon_discount_percent__gt=0) \
                  .order_by("-created_at")[:3]
    product_sale = B2CProduct.get_active_objects().filter(discount_percent__gt=0)\
        .exclude(coupon_dates__contains=now().date()).order_by("-created_at")[:3]

    if country:
        products = products.filter(company__country=country)
        top_product_list = top_product_list.filter(company__country=country)
        coupons = coupons.filter(company__country=country)
        product_sale = product_sale.filter(company__country=country)

    return render_to_response("centerpokupok/index.html", {'coupons': coupons, "newProducrList": products,
                                             "topPoductList": top_product_list, "productsSale": product_sale,
                                             'country': country},
                              context_instance=RequestContext(request))


def about(request):
    return render_to_response("centerpokupok/About/About.html")


def registration(request, form, auth_form):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/")

    if request.POST.get('Register', None):
        form = RegistrationFormUniqueEmail(request.POST)
        if form.is_valid() and request.POST.get('tos', None):
            cleaned = form.cleaned_data
            reg_view = RegistrationView()
            try:
                reg_view.register(request, **cleaned)
                return render_to_response("registration/registration_complete.html", locals())
            except ValueError:
                return render_to_response("registration/registration_closed.html")
        else:
            if not request.POST.get('tos', None):
                form.errors.update({"rules": _("Agreement with terms is required")})

    if request.POST.get('Login', None):
        auth_form = AuthenticationForm(request, data=request.POST)
        if auth_form.is_valid():
            user = authenticate(email=request.POST.get("username", ""), password=request.POST.get("password", ""))
            login(request, user)
            try:
                cabinet = Cabinet.objects.get(user=user.pk)
            except ObjectDoesNotExist:
                cabinet = Cabinet(user=user, create_user=user)
                cabinet.save()

            return HttpResponseRedirect(request.GET.get('next', '/'))

    return render_to_response("centerpokupok/Registr/registr.html", locals(), context_instance=RequestContext(request))


def user_logout(request):
    logout(request)
    return HttpResponseRedirect("/")
