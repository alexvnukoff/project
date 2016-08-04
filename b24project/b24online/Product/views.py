# -*- encoding: utf-8 -*-

import sys
import json
import logging

from django.db import transaction
from django.db.models import Q, Count
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now
from django.views.generic import (DetailView, ListView, View,
                                  TemplateView)
from guardian.shortcuts import get_objects_for_user
from guardian.mixins import LoginRequiredMixin

from b24online.cbv import ItemsList, ItemDetail, ItemUpdate, ItemCreate, \
                   ItemDeactivate, GalleryImageList, DeleteGalleryImage, \
                   DeleteDocument, DocumentList
from b24online.models import (B2BProduct, Company, Chamber, Country,
    B2BProductCategory, DealOrder, Deal, DealItem, Organization, Producer)
from centerpokupok.models import B2CProduct, B2CProductCategory
from b24online.Product.forms import (B2BProductForm, AdditionalPageFormSet,
    B2CProductForm, B2_ProductBuyForm, DealPaymentForm, DealListFilterForm,
    DealItemFormSet, DealOrderedFormSet, B2BProductFormSet, B2CProductFormSet,
    ProducerForm)
from paypal.standard.forms import PayPalPaymentsForm
from usersites.models import UserSite
from b24online.utils import (get_current_organization, get_permitted_orgs,
                             MTTPTreeBuilder)

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


class B2BProductUpdateList(B2BProductList):
    url_paginator = "products:b2b_product_update_paginator"
    paginate_by = 20
    template_name = 'b24online/Products/contentUpdate.html'

    def ajax(self, request, *args, **kwargs):
        self.template_name = 'b24online/Products/contentUpdatePage.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'b24online/Products/contentUpdate.html'

    def get_queryset(self):
        queryset = super(B2BProductUpdateList, self).get_queryset()
        current_org = self._current_organization
        if current_org is not None:
            queryset = self.model.get_active_objects()\
                .filter(company_id=current_org)\
                .order_by(*self._get_sorting_params())
        else:
            queryset = queryset.none()
        return queryset

    def get_context_data(self, **kwargs):
        context = super(B2BProductUpdateList, self).get_context_data(**kwargs)

        self.item_formset = B2BProductFormSet(
            queryset=context['page_obj'].object_list,
            data=self.request.POST,
            files=self.request.FILES,
        ) if self.request.method == 'POST' else \
            B2BProductFormSet(
                queryset=context['page_obj'].object_list
            )

        context.update({
            'current_organization': get_current_organization(self.request),
            'item_formset': self.item_formset,
        })
        return context

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data(**kwargs)
        if self.item_formset.is_valid():
            self.item_formset.save()
            return HttpResponseRedirect(self.request.path)
        return self.render_to_response(context)


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


class B2CProductUpdateList(B2CProductList):
    url_paginator = "products:b2c_product_update_paginator"
    paginate_by = 10
    template_name = 'b24online/Products/contentUpdateB2C.html'

    def ajax(self, request, *args, **kwargs):
        self.template_name = 'b24online/Products/contentUpdatePageB2C.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'b24online/Products/contentUpdateB2C.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        current_org = self._current_organization
        if current_org is not None:
            queryset = self.model.get_active_objects()\
                .filter(company_id=current_org)\
                .order_by(*self._get_sorting_params())
        else:
            queryset = queryset.none()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.item_formset = B2CProductFormSet(
            queryset=context['page_obj'].object_list,
            data=self.request.POST,
            files=self.request.FILES,
        ) if self.request.method == 'POST' else \
            B2CProductFormSet(
                queryset=context['page_obj'].object_list
            )

        context.update({
            'current_organization': get_current_organization(self.request),
            'item_formset': self.item_formset,
        })
        return context

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data(**kwargs)
        if self.item_formset.is_valid():
            self.item_formset.save()
            return HttpResponseRedirect(self.request.path)
        return self.render_to_response(context)


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
        if self.is_filtered():
            return self.get_filtered_items().sort(*self._get_sorting_params())

        queryset = self.model.get_active_objects().filter(
                is_active=True,
                coupon_dates__contains=now().date(),
                coupon_discount_percent__gt=0
                ).order_by(*self._get_sorting_params())

        return self.optimize_queryset(queryset)


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
        self.imageslist = request.POST.getlist('additional_images')

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

        if form.cleaned_data['additional_images']:
            form.instance.additional_images = self.imageslist

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


class B2_ProductBuy(ItemDetail):
    model = None
    template_name = None
    current_section = None
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
                reverse('products:deal_order_basket'))
        context.update({'form': form})
        return self.render_to_response(context)

    def get_context_data(self, request, **kwargs):
        self.object = self.get_object()
        return super(B2_ProductBuy, self).get_context_data(**kwargs)


class B2BProductBuy(B2_ProductBuy):
    model = B2BProduct
    template_name = 'b24online/Products/buyB2BProduct.html'
    current_section = _('Products B2B')


class B2CProductBuy(B2_ProductBuy):
    model = B2CProduct
    template_name = 'b24online/Products/buyB2CProduct.html'
    current_section = _('Products B2C')


class DealOrderList(LoginRequiredMixin, ListView):
    """
    Deal Orders list.
    """
    model = DealOrder
    template_name = 'b24online/Products/dealOrderList.html'
    current_section = _('Basket')
    item_formset = None

    @classmethod
    def get_deal_items_formset(cls, deal):
        """
        Construct the formset for Deal items.
        """
        assert isinstance(deal, Deal), _('Invalid parameter')
        return DealItemFormSet(queryset=deal.get_items())

    def dispatch(self, request, *args, **kwargs):
        """
        Define if the Order status was has been set for simple filter or
        basket.

        If the basket was requested set the template.
        """
        self.status = self.kwargs.get('status')
        self.is_basket = self.status == 'basket'
        if self.is_basket:
            self.template_name = 'b24online/Products/dealOrderBasket.html'
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super(DealOrderList, self).get_queryset()
        qs = qs.filter(
            (Q(customer_type=DealOrder.AS_PERSON) & \
             Q(created_by=self.request.user)) | \
            (Q(customer_type=DealOrder.AS_ORGANIZATION) & \
             Q(customer_organization__in=get_permitted_orgs(
                 self.request.user))))
        if self.is_basket:
            qs = qs.filter(order_deals__status=Deal.DRAFT)\
                .annotate(deals_amount=Count('order_deals'))\
                .filter(deals_amount__gt=0)
        elif self.status:
            qs = qs.filter(status=self.status)
        qs = qs.prefetch_related('customer_organization', 'created_by')

        self.items_qs = DealItem.objects.filter(deal__status=Deal.DRAFT,
            deal__deal_order__in=qs)

        return qs

    def get_context_data(self, **kwargs):
        context = super(DealOrderList, self).get_context_data(**kwargs)

        # Data: orders, deals and deals products
        deal_orders = context.get('object_list') or DealOrder.objects.none()
        total_cost_data = Deal.get_qs_cost(
            Deal.objects.filter(deal_order__in=deal_orders, status=Deal.DRAFT)
        )
        items_qs = DealItem.objects.filter(
            deal__status=Deal.DRAFT,
            deal__deal_order__in=deal_orders
        )

        # Formsets for deals products
        self.item_formset = DealItemFormSet(
            queryset=items_qs,
            data=self.request.POST
        ) if self.request.method == 'POST' else \
            DealItemFormSet(queryset=items_qs)
        item_formset_dict = dict((item_form.instance.pk, item_form) \
            for item_form in self.item_formset)

        # Updated context
        context.update({
            'item_formset': self.item_formset,
            'item_formset_dict': item_formset_dict,
            'total_cost_data': total_cost_data,
        })
        return context

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data(**kwargs)
        if self.item_formset and self.item_formset.is_valid():
            self.item_formset.save()
            return HttpResponseRedirect(
                reverse('products:deal_order_basket'))
        return self.render_to_response(context)


class DealOrderDetail(LoginRequiredMixin, ItemDetail):
    model = DealOrder
    template_name = 'b24online/Products/dealOrderDetail.html'
    current_section = _('Deals history')


class DealOrderPayment(LoginRequiredMixin, ItemDetail):
    model = DealOrder
    template_name = 'b24online/Products/dealOrderDetail.html'
    current_section = _('Deals history')

    def get(self, request, *args, **kwargs):
        item = self.get_object()
        item.pay()
        return HttpResponseRedirect(
            reverse('products:deal_order_detail',
                kwargs={'pk': item.pk}))


class DealList(LoginRequiredMixin, ItemsList):
    model = Deal
    template_name = 'b24online/Products/dealList.html'
    current_section = _('Deals history')
    form_class = DealListFilterForm
    url_paginator = 'products:deal_list_paginator'
    paginate_by = 10
    sortField1 = 'created_at'
    order1 = 'asc'
    by_status = None

    def _get_sorting_params(self):
        return ['created_at',]

    def get_queryset(self):
        qs = super(DealList, self).get_queryset()
        current_organization = get_current_organization(self.request)
        if isinstance(current_organization, Company):
            qs = qs.filter(supplier_company=current_organization)
            self.by_status = self.kwargs.get('status') or \
                self.request.GET.get('status')
            if self.by_status:
                qs = qs.filter(status=self.by_status)
        else:
            return Deal.objects.none()
        return qs

    def get_context_data(self, **kwargs):
        qs = self.object_list
        is_filtered = False
        if 'filter' in self.request.GET:
            form = self.form_class(data=self.request.GET)
            if form.is_valid():
                is_filtered = True
                qs = form.filter(qs)
        else:
            form = self.form_class()
        total_cost_data = Deal.get_qs_cost(qs)
        self.object_list = qs
        context = super(DealList, self).get_context_data(**kwargs)

        if self.by_status == 'ordered':
            items_qs = context['page_obj'].object_list
            deal_formset = DealOrderedFormSet(
                queryset=items_qs,
                data=self.request.POST
            ) if self.request.method == 'POST' else \
                DealOrderedFormSet(queryset=items_qs)
            context.update({'deal_formset': deal_formset})

        context.update({
            'current_organization': get_current_organization(self.request),
            'form': form,
            'is_filtered': is_filtered,
            'total_cost_data': total_cost_data,
        })

        if self.by_status == Deal.ORDERED:
            if self.request.is_ajax():
                self.template_name = \
                    'b24online/Products/dealListOrderedBase.html'
            else:
                self.template_name = 'b24online/Products/dealListOrdered.html'
        elif self.request.is_ajax():
            self.template_name = 'b24online/Products/dealListBase.html'
        return context

    def render_to_response(self, context, **response_kwargs):
        return self.response_class(
            request=self.request,
            template=self.get_template_names(),
            context=context,
            using=self.template_engine,
            **response_kwargs
        )


class DealDetail(LoginRequiredMixin, ItemDetail):
    model = Deal
    template_name = 'b24online/Products/dealDetail.html'
    current_section = _('Deals history')

    def get_queryset(self):
        return super().get_queryset().prefetch_related('deal_order',
            'supplier_company')


class DealPayment(LoginRequiredMixin, ItemDetail):
    model = Deal
    template_name = 'b24online/Products/dealPayment.html'
    current_section = _('Deals history')
    form_class = DealPaymentForm
    success_url = reverse_lazy('products:deal_order_basket')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request)
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request, instance=self.object, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(self.success_url)
        return self.render_to_response(self.get_context_data(form=form))


class DealPayPal(LoginRequiredMixin, ItemDetail):
    model = Deal
    template_name = 'b24online/Products/dealPayPal.html'
    current_section = _('Deals history')
    success_url = reverse_lazy('products:deal_order_basket')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['deal'] = self.object
        if self.object.supplier_company.company_paypal_account:
            paypal_dict = {
                "business": self.object.supplier_company.company_paypal_account,
                "amount": self.object.total_cost,
                "item_number": self.object,
                "item_name": self.object,
                "no_shipping": 0,
                "quantity": 1,
                "currency_code": self.object.currency
            }
            paypal_form = PayPalPaymentsForm(initial=paypal_dict)
            context['paypal_form'] = paypal_form
        return context


class DealItemDetail(LoginRequiredMixin, ItemDetail):
    model = DealItem
    template_name = 'b24online/Products/dealItemDetail.html'
    current_section = _('Deals history')


class DealItemDelete(LoginRequiredMixin, ItemDetail):
    model = DealItem
    template_name = 'b24online/Products/dealDetail.html'
    current_section = _('Deals history')

    def get(self, request, *args, **kwargs):
        item = self.get_object()
        next = request.GET.get('next',
            reverse('products:deal_detail',
                kwargs={'item_id': item.deal.pk}))
        if item.deal.status == Deal.DRAFT \
            and item.deal.deal_order.status == DealOrder.DRAFT:
            item.delete()
        return HttpResponseRedirect(next)


def category_tree_json(request, b2_type='b2b'):
    """
    Return the json-ed tree of categories (B2B or B2C).
    """

    model_class = B2CProductCategory if b2_type == 'b2c' \
        else B2BProductCategory

    existed = []
    if 'content_type_id' in request.GET and 'item_id' in request.GET:
        content_type_id = request.GET['content_type_id']
        item_id = request.GET['item_id']
        try:
            content_type = ContentType.objects.get(pk=content_type_id)
        except ContentType.DoesNotExist:
            pass
        else:
            item_model_class = content_type.model_class()
            if item_id:
                try:
                    item = item_model_class.objects.get(pk=item_id)
                except item_model_class.DoesNotExist:
                    pass
                else:
                    if b2_type == 'b2c':
                        existed = [p.id for p in item.b2c_categories.all()]
                    elif b2_type == 'b2b':
                        existed = [p.id for p in item.b2b_categories.all()]

    def extract_data_fn(node):
        """
        Extract the node info for jstree fiels.
        """
        node_info = {'id': node.id, 'text': node.name,}
        if existed and node.id in existed:
            node_info.setdefault('state', {})['selected'] = True
        return node_info

    tree_builder = MTTPTreeBuilder(
        model_class,
        extract_data_fn=extract_data_fn,
    )
    data = tree_builder()
    return HttpResponse(
        json.dumps(data),
        content_type='application/json'
    )


@login_required
def category_tree_demo(request, b2_type='b2b'):

    def extract_data_fn(node):
        return {
            'id': node.id,
            'text': node.name,
        }
    context = {}
    model_class = B2CProductCategory if b2_type == 'b2c' \
        else B2BProductCategory
    tree_builder = MTTPTreeBuilder(
        model_class,
        extract_data_fn=extract_data_fn,
    )
    data = tree_builder()

    context.update({'tree_data': json.dumps(data)})
    return render_to_response(
        'b24online/Products/category_tree_demo.html',
        context,
        context_instance=RequestContext(request)
    )


class ProducerList(LoginRequiredMixin, ItemsList):
    model = Producer
    template_name = 'b24online/Products/producerList.html'
    current_section = _('Producers')
    url_paginator = 'products:producer_list_paginator'
    paginate_by = 10
    sortField1 = 'name'
    order1 = 'asc'

    def ajax(self, request, *args, **kwargs):
        self.template_name = 'b24online/Products/producerListContent.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'b24online/Products/producerList.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm('b24online.change_producer'):
            return HttpResponseRedirect(reverse('denied'))
        return super(ProducerList, self).dispatch(request, *args, **kwargs)

    def _get_sorting_params(self):
        return ['name',]

    def get_queryset(self):
        self.current_organization = get_current_organization(self.request)
        return Producer.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ProducerList, self).get_context_data(**kwargs)
        context.update({
            'current_organization': self.current_organization,
        })
        return context


class ProducerCreate(LoginRequiredMixin, ItemCreate):
    model = Producer
    form_class = ProducerForm
    template_name = 'b24online/Products/producerForm.html'
    success_url = reverse_lazy('products:producer_list')
    org_required = False
    current_section = _('Producers')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm('b24online.change_producer'):
            return HttpResponseRedirect(reverse('denied'))
        self.object = None
        return super(ProducerCreate, self)\
            .dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        form = self.form_class(
            data=request.POST,
            files=request.FILES
        )
        if form.is_valid():
            form.save()
            form.instance.upload_logo()
            return HttpResponseRedirect(self.success_url)
        return self.render_to_response(self.get_context_data(form=form))


class ProducerUpdate(LoginRequiredMixin, ItemUpdate):
    model = Producer
    form_class = ProducerForm
    template_name = 'b24online/Products/producerForm.html'
    success_url = reverse_lazy('products:producer_list')
    current_section = _('Producers')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm('b24online.change_producer'):
            return HttpResponseRedirect(reverse('denied'))
        self.object = self.get_object()
        return super(ProducerUpdate, self)\
            .dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(instance=self.object)
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        form = self.form_class(
            instance=self.object,
            data=request.POST,
            files=request.FILES
        )
        if form.is_valid():
            form.save()
            form.instance.upload_logo()
            return HttpResponseRedirect(self.success_url)
        return self.render_to_response(self.get_context_data(form=form))


class ProducerDelete(LoginRequiredMixin, DetailView):
    model = Producer
    template_name = 'b24online/Products/producerForm.html'
    current_section = _('Producers')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm('b24online.change_producer'):
            return HttpResponseRedirect(reverse('denied'))
        return super(ProducerDelete, self)\
            .dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # FIXME: add the notification
        item = self.get_object()
        if item:
            item.delete()
        next = reverse('products:producer_list')
        return HttpResponseRedirect(next)
