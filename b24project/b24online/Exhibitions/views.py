from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.db import transaction
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _

from b24online.cbv import ItemsList, ItemDetail, ItemUpdate, ItemCreate, ItemDeactivate, GalleryImageList, \
    DeleteGalleryImage, DocumentList, DeleteDocument
from b24online.models import Exhibition, Branch, Organization
from b24online.Exhibitions.forms import AdditionalPageFormSet, ExhibitionForm


class ExhibitionList(ItemsList):
    # pagination url
    url_paginator = "exhibitions:paginator"
    url_my_paginator = "exhibitions:my_main_paginator"

    # Lists of required scripts and styles for ajax request
    styles = [
        settings.STATIC_URL + 'b24online/css/news.css',
        settings.STATIC_URL + 'b24online/css/company.css'
    ]

    sortFields = {
        'date': 'created_at',
        'name': 'title'
    }

    addUrl = 'exhibitions:add'

    # allowed filter list
    # filter_list = ['tpp', 'country', 'company', 'branch']

    @property
    def current_section(self):
        return _("Exhibitions")

    model = Exhibition

    def ajax(self, request, *args, **kwargs):
        self.template_name = 'b24online/Exhibitions/contentPage.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'b24online/Exhibitions/index.html'

    def optimize_queryset(self, queryset):
        return queryset.select_related('country').prefetch_related('organization')

    def get_queryset(self):
        queryset = super(ExhibitionList, self).get_queryset()

        if self.is_my():
            current_org = self._current_organization

            if current_org is not None:
                queryset = self.model.get_active_objects().filter(organization_id=current_org)
            else:
                queryset = queryset.none()

        return queryset


class ExhibitionDetail(ItemDetail):
    model = Exhibition
    template_name = 'b24online/Exhibitions/detailContent.html'

    current_section = _("Exhibitions")
    addUrl = 'exhibitions:add'


class ExhibitionDelete(ItemDeactivate):
    model = Exhibition


class ExhibitionUpdate(ItemUpdate):
    model = Exhibition
    form_class = ExhibitionForm
    template_name = 'b24online/Exhibitions/addForm.html'
    success_url = reverse_lazy('exhibitions:main')

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

        if form.changed_data:

            if 'start_date' in form.changed_data or 'end_date' in form.changed_data:
                form.instance.dates = (form.cleaned_data['start_date'], form.cleaned_data['end_date'])

            if 'longitude' in form.changed_data or 'latitude' in form.changed_data:
                form.instance.metadata['location'] = "{0},{1}".format(
                    form.cleaned_data['latitude'],
                    form.cleaned_data['longitude']
                )

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


class ExhibitionCreate(ItemCreate):
    model = Exhibition
    form_class = ExhibitionForm
    template_name = 'b24online/Exhibitions/addForm.html'
    success_url = reverse_lazy('exhibitions:main')

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

        form.instance.metadata = {
            'location': '%s,%s' % (form.cleaned_data['latitude'], form.cleaned_data['longitude'])
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


class ExhibitionGalleryImageList(GalleryImageList):
    owner_model = Exhibition
    namespace = 'exhibitions'


class DeleteExhibitionGalleryImage(DeleteGalleryImage):
    owner_model = Exhibition


class ExhibitionDocumentList(DocumentList):
    owner_model = Exhibition
    namespace = 'exhibitions'


class DeleteExhibitionDocument(DeleteDocument):
    owner_model = Exhibition

