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


def wall(request):
    organization = get_current_site().user_site.organization
    proposals = BusinessProposal.get_active_objects().filter(organization=organization)
    news = News.get_active_objects().filter(organization=organization)
    exhibitions = Exhibition.get_active_objects().filter(organization=organization)

    if isinstance(organization, Company):
        b2c_products = B2CProduct.get_active_objects()\
            .filter(company=organization).order_by('-show_on_main')
        b2c_coupons = B2CProduct.get_active_objects().filter(company=organization,
                                                             coupon_dates__contains=now().date(),
                                                             coupon_discount_percent__gt=0).order_by("-created_at")
        b2b_products = B2BProduct.get_active_objects().filter(company=organization)
    else:
        b2b_products = None
        b2c_products = None
        b2c_coupons = None

    current_section = ''

    template_params = {
        'current_section': current_section,
        'title': get_current_site().user_site.organization.name,
        'proposals': proposals,
        'news': news,
        'exhibitions': exhibitions,
        'b2c_coupons': b2c_coupons,
        'b2c_products': b2c_products,
        'b2b_products': b2b_products,
        'form': ContactForm()
    }
    template_name = "{template_path}/contentPage.html"
    site = get_current_site()
    try:
        user_site = site.user_site
        user_site.refresh_from_db()

        if user_site.user_template is not None:
            folder_template = user_site.user_template.folder_name
            template_name = template_name.format(template_path=folder_template)
        else:
            template_name = template_name.format(template_path='usersites')
    except ObjectDoesNotExist:
        template_name = template_name.format(template_path='usersites')

    return render(request, template_name, template_params)


class ProductJsonData(View):
    model_class = None
    search_index_model = None

    def get(self, request):
        cls = type(self)
        term = request.GET.get('term')
        organization = get_current_site().user_site.organization
        if term and len(term) > 2:
            qs = cls.model_class.objects.filter(
                name__icontains=term,
                is_active=True,
                company=organization,
            ).order_by('name')
        else:
            qs = cls.model_class.objects.none()
        data = [{'id': item.id, 'value': item.name, 'img': item.image.small} \
            for item in qs]
        return JsonResponse(data, safe=False)


class UsersitesRegistrationView(RegistrationView):
    """
    The custom RegistrationView for 'usersites'.
    """
    template_name = 'registration/registration_form.html'


class sendmessage(View):
    def get_object(self, queryset=None):
        return get_current_site().user_site.organization

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        form = ContactForm(request.POST)
        if form.is_valid():

            cd = form.cleaned_data
            if not self.object.email:
                email = 'admin@tppcenter.com'
                subject = _('This message was sent to company:')
            else:
                email = self.object.email
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


class ProfileUpdate(ItemUpdate, UserTemplateMixin):
    model = Profile
    form_class = ProfileForm
    # template_name = '{template_path}/profileForm.html'
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

