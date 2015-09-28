from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.db import transaction
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _

from tppcenter.cbv import ItemsList, ItemDetail, ItemUpdate, ItemCreate, ItemDeactivate, DeleteGalleryImage, \
    GalleryImageList, DocumentList, DeleteDocument
from b24online.models import InnovationProject, Branch, Organization
from tppcenter.Innov.forms import InnovationProjectForm, AdditionalPageFormSet


class InnovationProjectList(ItemsList):
    # pagination url
    url_paginator = "innov:paginator"
    url_my_paginator = "innov:my_main_paginator"

    # Lists of required scripts and styles for ajax request
    styles = [
        settings.STATIC_URL + 'tppcenter/css/news.css',
        settings.STATIC_URL + 'tppcenter/css/company.css'
    ]

    current_section = _("Innovation Project")
    addUrl = 'innov:add'

    # allowed filter list
    # filter_list = ['tpp', 'country', 'company', 'branch']

    model = InnovationProject

    def ajax(self, request, *args, **kwargs):
        self.template_name = 'Innov/contentPage.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'Innov/index.html'

    def optimize_queryset(self, queryset):
        return queryset.prefetch_related('organization', 'organization__countries')

    def get_queryset(self):
        queryset = super(InnovationProjectList, self).get_queryset()

        if self.is_my():
            current_org = self._current_organization

            if current_org is not None:
                queryset = self.model.get_active_objects().filter(organization=current_org)
            else:
                queryset = self.model.get_active_objects().filter(created_by=self.request.user, organization__isnull=True)

        return queryset


class InnovationProjectDetail(ItemDetail):
    model = InnovationProject
    template_name = 'Innov/detailContent.html'

    current_section = _("Innovation Project")
    addUrl = 'innov:add'

    def get_queryset(self):
        return super().get_queryset() \
            .prefetch_related('galleries', 'galleries__gallery_items')


class InnovationProjectDelete(ItemDeactivate):
    model = InnovationProject


class InnovationProjectUpdate(ItemUpdate):
    model = InnovationProject
    form_class = InnovationProjectForm
    template_name = 'Innov/addForm.html'
    success_url = reverse_lazy('innov:main')

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

        if branches:
            context_data['branches'] = Branch.objects.filter(pk__in=branches)

        return context_data

    def form_valid(self, form, additional_page_form):
        """
        Called if all forms are valid. Creates a Recipe instance along with
        associated Ingredients and Instructions and then redirects to a
        success page.
        """
        form.instance.updated_by = self.request.user

        if form.changed_data:
            if 'release_date' in form.changed_data:
                form.instance.metadata['release_date'] = form.cleaned_data['release_date'].strftime('%d/%m/%Y')

            if 'site' in form.changed_data:
                form.instance.metadata['site'] = form.cleaned_data['site']

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


class InnovationProjectCreate(ItemCreate):
    model = InnovationProject
    form_class = InnovationProjectForm
    template_name = 'Innov/addForm.html'
    success_url = reverse_lazy('innov:main')

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

        form.instance.metadata = {
            'release_date': form.cleaned_data['release_date'].strftime('%d/%m/%Y'),
            'site': form.cleaned_data['site'],
        }

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

        if branches:
            context_data['branches'] = Branch.objects.filter(pk__in=branches)

        return context_data

    def form_invalid(self, form, additional_page_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        context_data = self.get_context_data(form=form, additional_page_form=additional_page_form)
        return self.render_to_response(context_data)


class InnovGalleryImageList(GalleryImageList):
    owner_model = InnovationProject
    namespace = 'innov'


class DeleteInnovGalleryImage(DeleteGalleryImage):
    owner_model = InnovationProject


class InnovDocumentList(DocumentList):
    owner_model = InnovationProject
    namespace = 'innov'


class DeleteInnovDocument(DeleteDocument):
    owner_model = InnovationProject

