from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from django.views.generic import UpdateView, CreateView

from appl import func
from b24online.cbv import ItemsList, ItemDetail
from b24online.models import Tender, Organization, Branch


# from core.tasks import addNewTender
from tppcenter.Tenders.forms import TenderForm, AdditionalPageFormSet


class TenderList(ItemsList):
    #pagination url
    url_paginator = "tenders:paginator"
    url_my_paginator = "tenders:my_main_paginator"

    #Lists of required scripts and styles for ajax request
    styles = [
        settings.STATIC_URL + 'tppcenter/css/news.css',
        settings.STATIC_URL + 'tppcenter/css/company.css'
    ]

    current_section = _("Tenders")
    addUrl = 'tenders:add'

    #allowed filter list
    # filter_list = ['tpp', 'country', 'company', 'branch']

    sortFields = {
        'date': 'created_at',
        'name': 'title'
    }

    model = Tender

    def ajax(self, request, *args, **kwargs):
        self.template_name = 'Tenders/contentPage.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'Tenders/index.html'

    def optimize_queryset(self, queryset):
        return queryset.select_related('country').prefetch_related('organization')

    def get_queryset(self):
        queryset = super(TenderList, self).get_queryset()

        if self.is_my():
            current_org = self._current_organization

            if current_org is not None:
                queryset = self.model.objects.filter(organization_id=current_org)
            else:
                queryset = queryset.none()

        return queryset


class TenderDetail(ItemDetail):
    model = Tender
    template_name = 'Tenders/detailContent.html'

    current_section = _("Tenders")
    addUrl = 'tenders:add'


@login_required
def tenderForm(request, action, item_id=None):
    if item_id:
       if not Tender.active.get_active().filter(pk=item_id).exists():
         return HttpResponseNotFound()


    current_section = _("Tenders")
    tendersPage = ''

    if action == 'delete':
        tendersPage = deleteTender(request, item_id)

    if isinstance(tendersPage, HttpResponseRedirect) or isinstance(tendersPage, HttpResponse):
        return tendersPage

    templateParams = {
        'formContent': tendersPage,
        'current_section': current_section
    }

    return render_to_response('forms.html', templateParams, context_instance=RequestContext(request))


def deleteTender(request, item_id):
    item = Organization.objects.get(p2c__child=item_id)

    perm_list = item.getItemInstPermList(request.user)

    if 'delete_tender' not in perm_list:
        return func.permissionDenied()

    instance = Tender.objects.get(pk=item_id)
    instance.activation(eDate=now())
    instance.end_date = now()
    instance.reindexItem()




    return HttpResponseRedirect(request.GET.get('next'), reverse('tenders:main'))


class TenderUpdate(UpdateView):
    model = Tender
    form_class = TenderForm
    template_name = 'Tenders/addForm.html'
    success_url = reverse_lazy('tenders:main')

    # TODO: check permission
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        additional_page_form = AdditionalPageFormSet(instance=self.object)

        return self.render_to_response(self.get_context_data(form=form, additional_page_form=additional_page_form))

    def post(self, request, *args, **kwargs):
        """
            Handles POST requests, instantiating a form instance and its inline
            formsets with the passed POST variables and then checking them for
            validity.
            """
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        additional_page_form = AdditionalPageFormSet(self.request.POST, instance=self.object)

        if form.is_valid() and additional_page_form.is_valid():
            return self.form_valid(form, additional_page_form)
        else:
            return self.form_invalid(form, additional_page_form)

    def form_valid(self, form, additional_page_form):
        """
        Called if all forms are valid. Creates a Recipe instance along with
        associated Ingredients and Instructions and then redirects to a
        success page.
        """
        form.instance.updated_by = self.request.user

        with transaction.atomic():
            self.object = form.save()
            additional_page_form.instance = self.object

            for page_form in additional_page_form:
                if not page_form.instance.pk:
                    page_form.instance.created_by = self.request.user
                page_form.instance.updated_by = self.request.user

            additional_page_form.save()

        if form.changed_data:
            self.object.reindex()

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, additional_page_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """

        return self.render_to_response(self.get_context_data(form=form, additional_page_form=additional_page_form))

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        branches = context_data['form']['branches'].value()

        if branches:
            context_data['branches'] = Branch.objects.filter(pk__in=branches)

        return context_data


class TenderCreate(CreateView):
    model = Tender
    form_class = TenderForm
    template_name = 'Tenders/addForm.html'
    success_url = reverse_lazy('proposal:main')

    # TODO: check permission
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        additional_page_form = AdditionalPageFormSet()

        return self.render_to_response(self.get_context_data(form=form, additional_page_form=additional_page_form))

    def post(self, request, *args, **kwargs):
        """
            Handles POST requests, instantiating a form instance and its inline
            formsets with the passed POST variables and then checking them for
            validity.
            """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        additional_page_form = AdditionalPageFormSet(self.request.POST)

        if form.is_valid() and additional_page_form.is_valid():
            return self.form_valid(form, additional_page_form)
        else:
            return self.form_invalid(form, additional_page_form)

    def form_valid(self, form, additional_page_form):
        """
        Called if all forms are valid. Creates a Recipe instance along with
        associated Ingredients and Instructions and then redirects to a
        success page.
        """
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        form.instance.dates = (form.cleaned_data['start_date'], form.cleaned_data['end_date'])

        with transaction.atomic():
            organization_id = self.request.session.get('current_company', None)
            form.instance.organization = Organization.objects.get(pk=organization_id)

            self.object = form.save()

            additional_page_form.instance = self.object

            for page_form in additional_page_form:
                page_form.instance.created_by = self.request.user
                page_form.instance.updated_by = self.request.user

            additional_page_form.save()

        self.object.reindex()

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, additional_page_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        context_data = self.get_context_data(form=form, additional_page_form=additional_page_form)
        return self.render_to_response(context_data)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        branches = context_data['form']['branches'].value()

        if branches:
            context_data['branches'] = Branch.objects.filter(pk__in=branches)

        return context_data