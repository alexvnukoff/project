# -*- encoding: utf-8 -*-

import logging

from django.db import transaction
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.timezone import now
from django.views.generic import DetailView, ListView, View

from b24online.cbv import ItemsList, ItemDetail, ItemUpdate, ItemCreate, \
                   ItemDeactivate, GalleryImageList, DeleteGalleryImage, \
                   DeleteDocument, DocumentList
from b24online.models import (B2BProduct, Company, Chamber, Country, 
    B2BProductCategory, DealOrder, Deal, DealItem)
from centerpokupok.models import B2CProduct, B2CProductCategory
from b24online.Product.forms import (B2BProductForm, AdditionalPageFormSet, 
    B2CProductForm, B2_ProductBuyForm)
from paypal.standard.forms import PayPalPaymentsForm
from usersites.models import UserSite


logger = logging.getLogger(__name__)


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

    def ajax(self, request, *args, **kwargs):
        self.template_name = 'b24online/Products/contentPage.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'b24online/Products/index.html'

    def optimize_queryset(self, queryset):
        return queryset.prefetch_related('company__countries')

    def get_queryset(self):
        queryset = super(B2BProductList, self).get_queryset()

        if self.is_my():
            current_org = self._current_organization

            if current_org is not None:
                queryset = self.model.get_active_objects()\
                .filter(company_id=current_org)\
                .order_by(*self._get_sorting_params())
            else:
                queryset = queryset.none()

        return queryset


class B2CProductList(ItemsList):
    # pagination url
    url_paginator = "products:main_b2c_paginator"
    url_my_paginator = "products:my_b2c_paginator"

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
        context.update(
            update_url='updateB2C',
            delete_url='deleteB2C'
        )

        if not self.my:
            try:
                 # 23470 Expert Center ID
                context['slider'] = UserSite.objects.get(organization_id=23470)
            except UserSite.DoesNotExist:
                context['slider'] = None
        return context


    def ajax(self, request, *args, **kwargs):
        self.template_name = 'b24online/Products/contentPageB2C.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'b24online/Products/index_b2c.html'

    def optimize_queryset(self, queryset):
        return queryset.prefetch_related('company__countries')

    def get_queryset(self):
        queryset = super(B2CProductList, self).get_queryset()

        if self.is_my():
            current_org = self._current_organization

            if current_org is not None:
                queryset = self.model.get_active_objects()\
                .filter(company_id=current_org)\
                .order_by(*self._get_sorting_params())
            else:
                queryset = queryset.none()

        return queryset



class B2CPCouponsList(ItemsList):
    # pagination url
    url_paginator = "products:coupons_paginator"
    paginate_by = 13

    # Lists of required scripts and styles for ajax request
    scripts = []
    styles = []

    current_section = _("Products B2C")
    addUrl = 'products:addB2C'
    model = B2CProduct

    # allowed filter list
    # filter_list = ['tpp', 'country', 'company', 'branch']

    def get_context_data(self, **kwargs):
        context = super(B2CPCouponsList, self).get_context_data(**kwargs)
        context.update(
            update_url='updateB2C',
            delete_url='deleteB2C'
        )

        return context

    def ajax(self, request, *args, **kwargs):
        self.template_name = 'b24online/Products/contentPageB2C_coupons.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'b24online/Products/index_b2c_coupons.html'

    def get_queryset(self):
        queryset = super(B2CPCouponsList, self).get_queryset().filter(\
                                  coupon_dates__contains=now().date())\
                        .exclude(coupon_discount_percent__isnull=True)
        return queryset



class B2BProductDetail(ItemDetail):
    model = B2BProduct
    template_name = 'b24online/Products/detailContent.html'

    current_section = _("Products B2B")
    addUrl = 'products:add'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('company', \
                                            'company__countries')


class B2CProductDetail(ItemDetail):
    model = B2CProduct
    template_name = 'b24online/Products/detailContentB2C.html'

    current_section = _("Products B2C")
    addUrl = 'products:addB2C'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('company', \
                                            'company__countries')

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        if self.object.currency and self.object.cost and self.object.company.\
                                                      company_paypal_account:
            paypal_dict = {
                "business": self.object.company.company_paypal_account,
                "amount": self.object.get_discount_price,
                "notify_url": self.request.build_absolute_uri(),
                "return_url": self.request.build_absolute_uri(),
                "cancel_return": self.request.build_absolute_uri(),
                "item_number": self.object.pk,
                "item_name": self.object.name,
                "no_shipping": 0,
                "quantity": 1,
                "currency_code": self.object.currency
            }

            context_data['paypal_form'] = PayPalPaymentsForm(initial=paypal_dict)
        return context_data


class B2BProductDelete(ItemDeactivate):
    model = B2BProduct


class B2CProductDelete(ItemDeactivate):
    model = B2CProduct


def categories_list(request, model):
    parent = request.GET.get('parent', None)
    bread_crumbs = None

    # TODO: paginate?
    categories = model.objects.filter(parent=parent)

    if parent is not None:
        bread_crumbs = model.objects.get(pk=parent)\
                            .get_ancestors(ascending=False, include_self=True)

    template_params = {
        'object_list': categories,
        'bread_crumbs': bread_crumbs
    }

    return render_to_response('b24online/Products/categoryList.html',\
           template_params, context_instance=RequestContext(request))


class B2BProductCreate(ItemCreate):
    org_model = Company
    model = B2BProduct
    form_class = B2BProductForm
    template_name = 'b24online/Products/addForm.html'
    success_url = reverse_lazy('products:main')

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        additional_page_form = AdditionalPageFormSet()

        return self.render_to_response(self.get_context_data(form=form,\
                             additional_page_form=additional_page_form))

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
        context_data = self.get_context_data(form=form,\
             additional_page_form=additional_page_form)
        categories = form.cleaned_data.get('categories', None)

        if categories is not None:
            context_data['categories'] = B2BProductCategory.objects\
                                          .filter(pk__in=categories)

        return self.render_to_response(context_data)


class B2BProductUpdate(ItemUpdate):
    model = B2BProduct
    form_class = B2BProductForm
    template_name = 'b24online/Products/addForm.html'
    success_url = reverse_lazy('products:main')

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        additional_page_form = AdditionalPageFormSet(instance=self.object)

        return self.render_to_response(self.get_context_data(form=form,\
                            additional_page_form=additional_page_form))

    def post(self, request, *args, **kwargs):
        """
            Handles POST requests, instantiating a form instance and its inline
            formsets with the passed POST variables and then checking them for
            validity.
            """
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        additional_page_form = AdditionalPageFormSet(self.request.POST,\
                                                  instance=self.object)

        if form.is_valid() and additional_page_form.is_valid():
            return self.form_valid(form, additional_page_form)
        else:
            return self.form_invalid(form, additional_page_form)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        categories = context_data['form']['categories'].value()

        if categories:
            context_data['categories'] = B2BProductCategory.objects\
                                          .filter(pk__in=categories)

        return context_data

    def form_valid(self, form, additional_page_form):
        """
        Called if all forms are valid. Creates a Recipe instance along with
        associated Ingredients and Instructions and then redirects to a
        success page.
        """
        form.instance.updated_by = self.request.user

        if form.changed_data and 'sku' in form.changed_data:
            form.instance.metadata['stock_keeping_unit'] = form\
                                            .cleaned_data['sku']

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

            if 'image' in form.changed_data:
                self.object.upload_images()

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, additional_page_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """

        return self.render_to_response(self.get_context_data(form=form,\
                            additional_page_form=additional_page_form))


class B2CProductCreate(ItemCreate):
    org_model = Company
    model = B2CProduct
    form_class = B2CProductForm
    template_name = 'b24online/Products/addFormB2C.html'
    success_url = reverse_lazy('products:my_b2c')

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        additional_page_form = AdditionalPageFormSet()

        return self.render_to_response(self.get_context_data(form=form,\
                            additional_page_form=additional_page_form))

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

        if form.cleaned_data['start_coupon_date'] and \
                  form.cleaned_data['end_coupon_date'] \
                  and form.cleaned_data['coupon_discount_percent']:
            form.instance.coupon_dates = (form.cleaned_data['start_coupon_date'],\
                                            form.cleaned_data['end_coupon_date'])

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
        context_data = self.get_context_data(form=form,\
             additional_page_form=additional_page_form)
        categories = form.cleaned_data.get('categories', None)

        if categories is not None:
            context_data['categories'] = B2CProductCategory.objects\
                                          .filter(pk__in=categories)

        return self.render_to_response(context_data)


class B2CProductUpdate(ItemUpdate):
    model = B2CProduct
    form_class = B2CProductForm
    template_name = 'b24online/Products/addFormB2C.html'
    success_url = reverse_lazy('products:my_b2c')

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        additional_page_form = AdditionalPageFormSet(instance=self.object)

        return self.render_to_response(self.get_context_data(form=form,\
                            additional_page_form=additional_page_form))

    def post(self, request, *args, **kwargs):
        """
            Handles POST requests, instantiating a form instance and its inline
            formsets with the passed POST variables and then checking them for
            validity.
            """
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        additional_page_form = AdditionalPageFormSet(self.request.POST,\
                                                  instance=self.object)

        if form.is_valid() and additional_page_form.is_valid():
            return self.form_valid(form, additional_page_form)
        else:
            return self.form_invalid(form, additional_page_form)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        categories = context_data['form']['categories'].value()

        if categories:
            context_data['categories'] = B2CProductCategory.objects\
                                          .filter(pk__in=categories)

        return context_data

    def form_valid(self, form, additional_page_form):
        """
        Called if all forms are valid. Creates a Recipe instance along with
        associated Ingredients and Instructions and then redirects to a
        success page.
        """
        form.instance.updated_by = self.request.user

        if form.changed_data and 'sku' in form.changed_data:
            form.instance.metadata['stock_keeping_unit'] =\
                                    form.cleaned_data['sku']

        if form.cleaned_data['start_coupon_date'] and \
             form.cleaned_data['end_coupon_date'] and \
             form.cleaned_data['coupon_discount_percent']:

            form.instance.coupon_dates = (form.cleaned_data['start_coupon_date'], \
                                            form.cleaned_data['end_coupon_date'])
        else:
            form.instance.coupon_dates = None

        with transaction.atomic():
            self.object = form.save()
            additional_page_form.instance = self.object

            for page_form in additional_page_form:
                if not page_form.instance.created_by_id:
                    page_form.instance.created_by = self.request.user
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

        return self.render_to_response(self.get_context_data(form=form, \
                            additional_page_form=additional_page_form))


class B2BProductGalleryImageList(GalleryImageList):
    owner_model = B2BProduct
    namespace = 'products'


class DeleteB2BProductGalleryImage(DeleteGalleryImage):
    owner_model = B2BProduct


class B2BProductDocumentList(DocumentList):
    owner_model = B2BProduct
    namespace = 'products'


class DeleteB2BProductDocument(DeleteDocument):
    owner_model = B2BProduct


class B2BProductBuy(ItemDetail):
    model = B2BProduct
    template_name = 'b24online/Products/buyB2BProduct.html'
    current_section = _('Products B2B')
    form_class = B2_ProductBuyForm
    
    def get_queryset(self):
        return super().get_queryset()\
            .prefetch_related('company', 'company__countries')

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(request, **kwargs) or {}
        form = self.form_class(request, self.object)
        context.update({'form': form})
        return self.render_to_response(context)
                    
    def post(self, request, *args, **kwargs):
        context = self.get_context_data(request, **kwargs) or {}
        form = self.form_class(request, self.object, data=request.POST)
        if form.is_valid():
            item = form.save()
            return HttpResponseRedirect(
                reverse('products:deal_order_detail', 
                        kwargs={'pk': item.pk}))

        context.update({'form': form})
        return self.render_to_response(context)

    def get_context_data(self, request, **kwargs):
        self.object = self.get_object()
        return super(B2BProductBuy, self).get_context_data(**kwargs)


class B2CProductBuy(ItemDetail):
    model = B2CProduct
    template_name = 'b24online/Products/buyB2CProduct.html'
    current_section = _('Products B2C')
    success_url = reverse_lazy('products:main')

    def get_queryset(self):
        return super().get_queryset()\
            .prefetch_related('company', 'company__countries')


class DealOrderList(ListView):
    model = DealOrder
    template_name = 'b24online/Products/dealOrderList.html'
    current_section = _('Deals')


class DealOrderDetail(DetailView):
    model = DealOrder
    template_name = 'b24online/Products/dealOrderDetail.html'
    current_section = _('Deals')

    def get_context_data(self, **kwargs):
        context = super(DealOrderDetail, self).get_context_data(**kwargs)
        self.object = self.get_object()
        context.update({'item': self.object})
        return context


class DealOrderPayment(DetailView):
    model = DealOrder
    template_name = 'b24online/Products/dealOrderDetail.html'
    current_section = _('Deals')

    def get(self, request, *args, **kwargs):
        item = self.get_object()
        item.status = DealOrder.PAID
        item.save()
        return HttpResponseRedirect(
            reverse('products:deal_order_detail', 
                kwargs={'pk': item.pk}))


class DealList(ListView):
    model = Deal
    template_name = 'b24online/Products/dealList.html'
    current_section = _('Deals')


class DealDetail(DetailView):
    model = Deal
    template_name = 'b24online/Products/dealDetail.html'
    current_section = _('Deals')

    def get_context_data(self, **kwargs):
        context = super(DealDetail, self).get_context_data(**kwargs)
        self.object = self.get_object()
        context.update({'item': self.object})
        return context


class DealPayment(DetailView):
    model = Deal
    template_name = 'b24online/Products/dealDetail.html'
    current_section = _('Deals')

    def get(self, request, *args, **kwargs):
        item = self.get_object()
        item.status = DealOrder.PAID
        item.save()
        return HttpResponseRedirect(
            reverse('products:deal_order_detail', 
                kwargs={'pk': item.pk}))


class DealItemDelete(DetailView):
    model = DealItem
    template_name = 'b24online/Products/dealDetail.html'
    current_section = _('Deals')

    def get(self, request, *args, **kwargs):
        item = self.get_object()
        next = request.GET.get('next', 
            reverse('products:deal_detail', 
                kwargs={'pk': item.deal.pk}))        
        if item.deal.status == Deal.DRAFT \
            and item.deal.deal_order.status == DealOrder.DRAFT:    
            item.delete()
        return HttpResponseRedirect(next)

