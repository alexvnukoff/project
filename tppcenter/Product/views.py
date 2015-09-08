from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.utils.timezone import now
from django.views.generic import UpdateView, CreateView

from appl import func
from appl.models import Product
from b24online.cbv import ItemsList, ItemDetail
from b24online.models import B2BProduct, Company, Organization, B2BProductCategory
from centerpokupok.models import B2CProduct, B2CProductCategory
from tppcenter.Product.forms import B2BProductForm, AdditionalPageFormSet, B2CProductForm


class B2BProductList(ItemsList):
    # Pagination url
    url_paginator = "products:paginator"
    url_my_paginator = "products:my_main_paginator"

    # Lists of required scripts and styles for ajax request
    scripts = []
    styles = []

    paginate_by = 12

    current_section = _("Products B2B")
    addUrl = 'products:add'

    # Allowed filter list
    # filter_list = ['tpp', 'country', 'company', 'branch']

    model = B2BProduct

    def get_context_data(self, **kwargs):
        context = super(B2BProductList, self).get_context_data(**kwargs)
        context['update_url'] = 'update'

        return context

    def ajax(self, request, *args, **kwargs):
        self.template_name = 'Products/contentPage.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'Products/index.html'

    def optimize_queryset(self, queryset):
        return queryset.prefetch_related('company__countries')

    def get_queryset(self):
        queryset = super(B2BProductList, self).get_queryset()

        if self.is_my():
            current_org = self._current_organization

            if current_org is not None:
                queryset = queryset.filter(company_id=current_org)
            else:
                queryset = queryset.none()

        return queryset


class B2CProductList(ItemsList):
    # pagination url
    url_my_paginator = "products:my_main_b2c_paginator"

    # Lists of required scripts and styles for ajax request
    scripts = []
    styles = []

    paginate_by = 12

    current_section = _("Products B2C")
    addUrl = 'products:addB2C'

    # allowed filter list
    # filter_list = ['tpp', 'country', 'company', 'branch']

    model = B2CProduct

    def get_context_data(self, **kwargs):
        context = super(B2CProductList, self).get_context_data(**kwargs)
        context['update_url'] = 'updateB2C'

        return context

    def ajax(self, request, *args, **kwargs):
        self.template_name = 'Products/contentPage.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'Products/index.html'

    def get_queryset(self):
        queryset = super(B2CProductList, self).get_queryset()

        if self.request.user.is_authenticated() and not self.request.user.is_anonymous() and self.my:
            current_org = self._current_organization

            if current_org is not None:
                queryset = self.model.objects.filter(company_id=current_org)
            else:
                return queryset.none()

        return queryset.prefetch_related('company__countries')


class B2BProductDetail(ItemDetail):
    model = B2BProduct
    template_name = 'Products/detailContent.html'

    current_section = _("Products B2B")
    addUrl = 'products:add'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('company', 'company__countries')


class B2CProductDetail(ItemDetail):
    model = B2CProduct
    template_name = 'Products/detailContent.html'

    current_section = _("Products B2C")
    addUrl = 'products:addB2C'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('company', 'company__countries')


@login_required
def productForm(request, action, item_id=None):
    if item_id:
        if not Product.active.get_active().filter(pk=item_id).exists():
            return HttpResponseNotFound()

    current_section = _("Products")
    productsPage = ''

    if action == 'delete':
        productsPage = deleteProduct(request, item_id)

    if isinstance(productsPage, HttpResponseRedirect) or isinstance(productsPage, HttpResponse):
        return productsPage

    template_params = {
        'formContent': productsPage,
        'current_section': current_section,
        'item_id': item_id
    }

    return render_to_response('forms.html', template_params, context_instance=RequestContext(request))


def deleteProduct(request, item_id):
    item = Organization.objects.get(p2c__child=item_id)

    perm_list = item.getItemInstPermList(request.user)

    if 'delete_product' not in perm_list:
        return func.permissionDenied()

    instance = Product.objects.get(pk=item_id)
    instance.activation(eDate=now())
    instance.end_date = now()
    instance.reindexItem()

    return HttpResponseRedirect(request.GET.get('next'), reverse('products:main'))


def categories_list(request, model):
    parent = request.GET.get('parent', None)
    bread_crumbs = None

    # TODO: paginate?
    categories = model.objects.filter(parent=parent)

    if parent is not None:
        bread_crumbs = model.objects.get(pk=parent).get_ancestors(ascending=False, include_self=True)

    template_params = {
        'object_list': categories,
        'bread_crumbs': bread_crumbs
    }

    return render_to_response('Products/categoryList.html', template_params, context_instance=RequestContext(request))


class B2BProductCreate(CreateView):
    model = B2BProduct
    form_class = B2BProductForm
    template_name = 'Products/addForm.html'
    success_url = reverse_lazy('products:main')

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
        organization_id = self.request.session.get('current_company', None)
        company = Company.objects.get(pk=organization_id)
        form.instance.company = company
        form.instance.metadata = {'stock_keeping_unit': form.cleaned_data['sku']}

        with transaction.atomic():
            self.object = form.save()
            additional_page_form.instance = self.object

            for page_form in additional_page_form:
                page_form.instance.created_by = self.request.user
                page_form.instance.updated_by = self.request.user

            additional_page_form.save()

        self.object.reindex()
        self.object.upload_images()

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, additional_page_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        context_data = self.get_context_data(form=form, additional_page_form=additional_page_form)
        categories = form.cleaned_data.get('categories', None)

        if categories is not None:
            context_data['categories'] = B2BProductCategory.objects.filter(pk__in=categories)

        return self.render_to_response(context_data)


class B2BProductUpdate(UpdateView):
    model = B2BProduct
    form_class = B2BProductForm
    template_name = 'Products/addForm.html'
    success_url = reverse_lazy('products:main')

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

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        categories = context_data['form']['categories'].value()

        if categories:
            context_data['categories'] = B2BProductCategory.objects.filter(pk__in=categories)

        return context_data

    def form_valid(self, form, additional_page_form):
        """
        Called if all forms are valid. Creates a Recipe instance along with
        associated Ingredients and Instructions and then redirects to a
        success page.
        """
        form.instance.updated_by = self.request.user

        if form.changed_data and 'sku' in form.changed_data:
            form.instance.metadata['stock_keeping_unit'] = form.cleaned_data['sku']

        with transaction.atomic():
            self.object = form.save()
            additional_page_form.instance = self.object

            for page_form in additional_page_form:
                if not page_form.instance.pk:
                    page_form.instance.updated_by = self.request.user
                page_form.instance.updated_by = self.request.user

            additional_page_form.save()

        if form.changed_data:
            self.object.reindex()

            if 'image' in form.changed_data:
                self.object.upload_images()

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, additional_page_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """

        return self.render_to_response(self.get_context_data(form=form, additional_page_form=additional_page_form))


class B2CProductCreate(CreateView):
    model = B2CProduct
    form_class = B2CProductForm
    template_name = 'Products/addFormB2C.html'
    success_url = reverse_lazy('products:my_main_b2c')

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
        organization_id = self.request.session.get('current_company', None)
        form.instance.company = Company.objects.get(pk=organization_id)
        form.instance.metadata = {'stock_keeping_unit': form.cleaned_data['sku']}

        with transaction.atomic():
            self.object = form.save()
            additional_page_form.instance = self.object

            for page_form in additional_page_form:
                page_form.instance.created_by = self.request.user
                page_form.instance.updated_by = self.request.user

            additional_page_form.save()

        self.object.reindex()
        self.object.upload_images()

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, additional_page_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        context_data = self.get_context_data(form=form, additional_page_form=additional_page_form)
        categories = form.cleaned_data.get('categories', None)

        if categories is not None:
            context_data['categories'] = B2CProductCategory.objects.filter(pk__in=categories)

        return self.render_to_response(context_data)


class B2CProductUpdate(UpdateView):
    model = B2CProduct
    form_class = B2CProductForm
    template_name = 'Products/addFormB2C.html'
    success_url = reverse_lazy('products:my_main_b2c')

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

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        categories = context_data['form']['categories'].value()

        if categories:
            context_data['categories'] = B2CProductCategory.objects.filter(pk__in=categories)

        return context_data


    def form_valid(self, form, additional_page_form):
        """
        Called if all forms are valid. Creates a Recipe instance along with
        associated Ingredients and Instructions and then redirects to a
        success page.
        """
        form.instance.updated_by = self.request.user

        if form.changed_data and 'sku' in form.changed_data:
            form.instance.metadata['stock_keeping_unit'] = form.cleaned_data['sku']

        with transaction.atomic():
            self.object = form.save()
            additional_page_form.instance = self.object

            for page_form in additional_page_form:
                if not page_form.instance.created_by:
                    page_form.instance.updated_by = self.request.user
                page_form.instance.updated_by = self.request.user

            additional_page_form.save()

        if form.changed_data:
            self.object.reindex()

            if 'image' in form.changed_data:
                self.object.upload_images()

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, additional_page_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """

        return self.render_to_response(self.get_context_data(form=form, additional_page_form=additional_page_form))
