# -*- encoding: utf-8 -*-
import logging
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse_lazy
from django.http import JsonResponse, Http404, HttpResponseRedirect
from django.shortcuts import render
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from django.views.generic import View, TemplateView
from registration.backends.default.views import RegistrationView
from b24online.Leads.utils import GetLead
from b24online.cbv import ItemUpdate
from b24online.models import BusinessProposal, B2BProduct, News, Company, Profile, Exhibition
from b24online.utils import get_template_with_base_path
from centerpokupok.models import B2CProduct
from tpp.DynamicSiteMiddleware import get_current_site
from usersites.OrganizationPages.forms import ContactForm
from usersites.forms import ProfileForm
from usersites.mixins import UserTemplateMixin

logger = logging.getLogger(__name__)

def render_page(request, template, **kwargs):
    return render(request, get_template_with_base_path(template), kwargs)


class WallView(UserTemplateMixin, TemplateView):
    template_name = "{template_path}/contentPage.html"
    current_section = ""

    def get_company_content(self):
        self.proposals = BusinessProposal.get_active_objects().filter(
                organization=self.organization)

        self.news = News.get_active_objects().filter(
                organization=self.organization)

        self.exhibitions = Exhibition.get_active_objects().filter(
                organization=self.organization)

        if isinstance(self.organization, Company):
            self.b2c_products = B2CProduct.get_active_objects().filter(
                    company=self.organization).order_by('-show_on_main')

            self.b2c_coupons = B2CProduct.get_active_objects().filter(
                    company=self.organization,
                    coupon_dates__contains=now().date(),
                    coupon_discount_percent__gt=0).order_by("-created_at")

            self.b2b_products = B2BProduct.get_active_objects().filter(
                    company=self.organization)
        else:
            self.b2b_products = None
            self.b2c_products = None
            self.b2c_coupons = None

    def get_context_data(self, **kwargs):
        context = super(WallView, self).get_context_data(**kwargs)

        self.get_company_content()
        context = {
            'current_section': self.current_section,
            'organization': self.organization,
            'title': self.organization.name,
            'proposals': self.proposals,
            'news': self.news,
            'exhibitions': self.exhibitions,
            'b2c_coupons': self.b2c_coupons,
            'b2c_products': self.b2c_products,
            'b2b_products': self.b2b_products,
            'form': ContactForm()
        }

        return context


class UsersitesRegistrationView(RegistrationView):
    """
    The custom RegistrationView for 'usersites'.
    """
    template_name = 'registration/registration_form.html'


class sendmessage(UserTemplateMixin, View):
    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            if not self.organization.email:
                email = 'admin@tppcenter.com'
                subject = _('This message was sent to company:')
            else:
                email = self.organization.email
                subject = "B24online.com: New Lead from {0}".format(cd['name'])

            # Collecting lead
            getlead = GetLead(request)

            getlead.collect(
                url=cd['url_path'],
                realname=cd['name'],
                email=cd['email'],
                message=cd['message'],
                phone=cd['phone'],
                company_id=cd['co_id']
                )

            mail = EmailMessage(subject,
                    """
                    From: {0}
                    URL: {1}
                    Email: {2}
                    Phone: {3}

                    Message: {4}
                    """.format(
                        cd['name'],
                        cd['url_path'],
                        cd['email'],
                        cd['phone'],
                        cd['message']
                        ),
                    cd['email'],
                    [email]
                )
            mail.send()
            return HttpResponseRedirect(reverse_lazy('message_sent'))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    def get(self, request):
        raise Http404


class ProfileUpdate(UserTemplateMixin, ItemUpdate):
    model = Profile
    form_class = ProfileForm
    #template_name = '{template_path}/profileForm.html'
    template_name = 'usersites_templates/ibonds/profileForm.html'
    success_url = reverse_lazy('main')

    def form_invalid(self, form):
        return super().form_invalid(form)

    def get_object(self, queryset=None):
        try:
            return Profile.objects.get(user=self.request.user)
        except ObjectDoesNotExist:
            return Profile.objects.create(user=self.request.user)

    def form_valid(self, form):
        form.instance.birthday = form.cleaned_data.get('birthday', None)
        result = super().form_valid(form)

        if form.changed_data:
            self.object.reindex()

            if 'avatar' in form.changed_data:
                self.object.upload_images()

        return result


class MessageSent(UserTemplateMixin, TemplateView):
    template_name = '{template_path}/message_sent.html'


class ProductJsonData(UserTemplateMixin, View):
    model_class = None
    search_index_model = None

    def get(self, request):
        cls = type(self)
        term = request.GET.get('term')
        if term and len(term) > 2:
            qs = cls.model_class.objects.filter(
                name__icontains=term,
                is_active=True,
                company=self.organization,
            ).order_by('name')
        else:
            qs = cls.model_class.objects.none()
        data = [{'id': item.id, 'value': item.name, 'img': item.image.small} for item in qs]
        return JsonResponse(data, safe=False)
