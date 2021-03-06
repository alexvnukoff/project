from collections import OrderedDict

from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect, Http404
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.translation import ugettext as _

from b24online.models import AdditionalPage, Department
from tpp.DynamicSiteMiddleware import get_current_site
from usersites.OrganizationPages.forms import ContactForm
from usersites.cbv import ItemDetail
from usersites.mixins import UserTemplateMixin
from b24online.Leads.utils import GetLead
from b24online.models import (Company, News, BusinessProposal, Video,
                                       InnovationProject, Exhibition)


class PageDetail(UserTemplateMixin, ItemDetail):
    model = AdditionalPage
    template_name = '{template_path}/OrganizationPages/page.html'

    def get_queryset(self):
        return get_current_site().user_site.organization.additional_pages.all()

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['form'] = ContactForm()
        return context_data

class Contacts(UserTemplateMixin, DetailView):
    template_name = '{template_path}/OrganizationPages/contact.html'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context_data = self.get_context_data(object=self.object)

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

        context_data['form'] = form
        return self.render_to_response(context_data)

    def get_object(self, queryset=None):
        return get_current_site().user_site.organization

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['form'] = ContactForm()

        return context_data


class Structure(UserTemplateMixin, ListView):
    template_name = '{template_path}/OrganizationPages/structure.html'
    model = Department
    ordering = ['name']

    def get_queryset(self):
        return get_current_site().user_site.organization.departments.all()

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        departments = OrderedDict()

        for department in context_data['object_list']:
            vacancies = department.vacancies.filter(user__isnull=False).select_related('user', 'user__profile')
            departments[department.name] = [vacancy for vacancy in vacancies]

        context_data['current_section'] = _('Structure')
        context_data['departments'] = departments

        return context_data


class About(UserTemplateMixin, TemplateView):
    model = AdditionalPage
    template_name = '{template_path}/OrganizationPages/about.html'

    def get_queryset(self):
        return get_current_site().user_site.organization.additional_pages.all()


class Gallery(UserTemplateMixin, TemplateView):
    model = AdditionalPage
    template_name = '{template_path}/OrganizationPages/gallery.html'

    def get_queryset(self):
        return get_current_site().user_site.organization.additional_pages.all()


class CompanyView(UserTemplateMixin, DetailView):
    template_name = '{template_path}/OrganizationPages/company.html'
    model = Company
    current_section = ""

    def get_object(self, queryset=None):
        self.user = self.request.user
        self.company_id = self.kwargs.get(self.pk_url_kwarg)

    def get_context_data(self, **kwargs):
        context = super(CompanyView, self).get_context_data(**kwargs)

        try:
            company = Company.objects.get(pk=self.company_id)
        except Company.DoesNotExist as e:
            raise Http404

        context = {
            'current_section': self.current_section,
            'organization': self.organization,
            'company': company,
            'news': News.get_active_objects().filter(organization=company)[:2],
            'business_proposal': BusinessProposal.get_active_objects().filter(organization=company)[:2],
            'video': Video.get_active_objects().filter(organization=company)[:2],
            'innovation_project': InnovationProject.get_active_objects().filter(organization=company)[:2],
            'exhibition': Exhibition.get_active_objects().filter(organization=company)[:2]
        }

        return context

