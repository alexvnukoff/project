from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.db import transaction
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _

from b24online.models import Branch, BusinessProposal, Organization, BusinessProposalCategory
from tppcenter.BusinessProposal.forms import BusinessProposalForm, AdditionalPageFormSet
from tppcenter.cbv import ItemUpdate, ItemsList, ItemDetail, ItemCreate, ItemDeactivate, GalleryImageList, \
    DeleteGalleryImage, DocumentList, DeleteDocument


class BusinessProposalList(ItemsList):
    #pagination url
    url_paginator = "proposal:paginator"
    url_my_paginator = "proposal:my_main_paginator"

    #Lists of required scripts and styles for ajax request
    styles = [
        settings.STATIC_URL + 'tppcenter/css/news.css',
        settings.STATIC_URL + 'tppcenter/css/company.css'
    ]

    current_section = _("Business Proposal")
    addUrl = 'proposal:add'

    #allowed filter list
    # filter_list = {
    #     'chamber': Chamber,
    #     'country': Country,
    #     'branch': Branch,
    # }

    sortFields = {
        'date': 'created_at',
        'name': 'title'
    }

    model = BusinessProposal

    def ajax(self, request, *args, **kwargs):
        self.template_name = 'BusinessProposal/contentPage.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'BusinessProposal/index.html'

    def optimize_queryset(self, queryset):
        return queryset.prefetch_related('branches', 'organization', 'organization__countries')

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.is_my():
            current_org = self._current_organization

            if current_org is not None:
                queryset = self.model.active_objects.filter(organization_id=current_org)
            else:
                queryset = queryset.none()

        return queryset


class BusinessProposalDetail(ItemDetail):
    model = BusinessProposal
    template_name = 'BusinessProposal/detailContent.html'

    current_section = _("Business Proposal")
    addUrl = 'proposal:add'


class BusinessProposalDelete(ItemDeactivate):
    model = BusinessProposal


def bp_categories_list(request):
    parent = request.GET.get('parent', None)
    bread_crumbs = None

    # TODO: paginate?
    categories = BusinessProposalCategory.objects.filter(parent=parent)

    if parent is not None:
        bread_crumbs = BusinessProposalCategory.objects.get(pk=parent).get_ancestors(ascending=False, include_self=True)

    template_params = {
        'object_list': categories,
        'bread_crumbs': bread_crumbs
    }

    return render_to_response('BusinessProposal/BpCategoryList.html', template_params, context_instance=RequestContext(request))


class BusinessProposalUpdate(ItemUpdate):
    model = BusinessProposal
    form_class = BusinessProposalForm
    template_name = 'BusinessProposal/addForm.html'
    success_url = reverse_lazy('proposal:main')

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

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        branches = context_data['form']['branches'].value()
        categories = context_data['form']['categories'].value()

        if branches:
            context_data['branches'] = Branch.objects.filter(pk__in=branches)

        if categories:
            context_data['categories'] = BusinessProposalCategory.objects.filter(pk__in=categories)

        return context_data

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


class BusinessProposalCreate(ItemCreate):
    model = BusinessProposal
    form_class = BusinessProposalForm
    template_name = 'BusinessProposal/addForm.html'
    success_url = reverse_lazy('proposal:main')

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

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        branches = context_data['form']['branches'].value()
        categories = context_data['form']['categories'].value()

        if branches:
            context_data['branches'] = Branch.objects.filter(pk__in=branches)

        if categories:
            context_data['categories'] = BusinessProposalCategory.objects.filter(pk__in=categories)

        return context_data

    def form_invalid(self, form, additional_page_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        context_data = self.get_context_data(form=form, additional_page_form=additional_page_form)
        return self.render_to_response(context_data)


class BPGalleryImageList(GalleryImageList):
    owner_model = BusinessProposal
    namespace = 'proposal'


class DeleteBPGalleryImage(DeleteGalleryImage):
    owner_model = BusinessProposal


class BPDocumentList(DocumentList):
    owner_model = BusinessProposal
    namespace = 'proposal'


class DeleteBPDocument(DeleteDocument):
    owner_model = BusinessProposal

