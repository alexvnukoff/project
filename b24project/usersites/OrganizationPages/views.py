from collections import OrderedDict

from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, ListView
from django.utils.translation import ugettext as _

from b24online.models import AdditionalPage, Department
from tpp.DynamicSiteMiddleware import get_current_site
from usersites.OrganizationPages.forms import ContactForm
from usersites.cbv import ItemDetail
from usersites.mixins import UserTemplateMixin


class PageDetail(UserTemplateMixin, ItemDetail):
    model = AdditionalPage
    template_name = '{template_path}/OrganizationPages/page.html'

    def get_queryset(self):
        return get_current_site().user_site.organization.additional_pages.all()


class Contacts(UserTemplateMixin, DetailView):
    template_name = '{template_path}/OrganizationPages/contact.html'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context_data = self.get_context_data(object=self.object)

        form = ContactForm(request.POST)

        if form.is_valid():
            if not self.object.email:
                email = 'admin@tppcenter.com'
                subject = _('This message was sent to company:')
            else:
                email = self.object.email
                subject = "New message from %s" % form.cleaned_data.get('name')

            mail = EmailMessage(subject, form.cleaned_data.get('message'), form.cleaned_data.get('email'), [email])
            mail.send()

            return HttpResponseRedirect(reverse('pages:contacts'))

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