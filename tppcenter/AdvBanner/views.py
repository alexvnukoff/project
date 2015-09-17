import json
from decimal import Decimal

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views.generic import ListView, CreateView, DetailView

from appl import func
from b24online.models import BannerBlock, Banner, AdvertisementPrices, AdvertisementOrder, Organization, \
    AdvertisementTarget

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import HttpResponse, HttpResponseRedirect
from tppcenter.AdvBanner.forms import BannerForm
from tppcenter.cbv import ItemCreate


class BannerBlockList(ListView):
    template_name = 'AdvBanner/index.html'
    context_object_name = 'blocks'
    ordering = 'block_type, name'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return BannerBlock.objects.filter(block_type__in=['b2c', 'b2b'])

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        sites = {}

        for block in context_data['blocks']:
            site_name = block.get_block_type_display()

            if site_name not in sites:
                sites[site_name] = []

            sites[site_name].append(block)

            context_data['sites'] = sites

        return context_data


class CreateBanner(ItemCreate):
    model = Banner
    form_class = BannerForm
    template_name = 'AdvBanner/addForm.html'
    success_url = None

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.block = BannerBlock.objects.get(pk=kwargs.pop('block_id'), block_type__in=['b2c', 'b2b'])
        self.organization = Organization.objects.get(pk=request.session.get('current_company', None))

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['block'] = self.block

        return kwargs

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        form.instance.site = None
        form.instance.is_active = False
        form.instance.dates = (form.cleaned_data['start_date'], form.cleaned_data['end_date'])
        form.instance.block = self.block

        with transaction.atomic():
            self.object = form.save()
            price_filter = None
            targets = []

            for valid_filter in ['branches', 'country', 'chamber']:
                obj_list = form.cleaned_data.get(valid_filter, None)

                if obj_list:
                    model_type = ContentType.objects.get_for_model(obj_list[0])

                    if price_filter is not None:
                        price_filter = price_filter | Q(content_type__pk=model_type.pk, object_id__in=obj_list)
                    else:
                        price_filter = Q(content_type__pk=model_type.pk, object_id__in=obj_list)

                    targets += [
                        AdvertisementTarget(
                            advertisement_item=self.object,
                            item=obj,
                            created_by=self.request.user,
                            updated_by=self.request.user) for obj in obj_list
                        ]

            AdvertisementTarget.objects.bulk_create(targets)

            prices = AdvertisementPrices.objects.filter(price_filter, advertisement_type='banner', dates__contains=now())
            days = (form.cleaned_data['end_date'] - form.cleaned_data['start_date']).days
            total_cost = sum([target.price for target in prices]) * Decimal(days) * Decimal(self.block.factor)
            order = AdvertisementOrder.objects.create(advertisement=self.object,
                                                      total_cost=total_cost,
                                                      purchaser=self.organization,
                                                      dates=(form.cleaned_data['start_date'], form.cleaned_data['end_date']),
                                                      price_factor=self.block.factor,
                                                      created_by=self.request.user,
                                                      updated_by=self.request.user)
            order.price_components.add(*prices)

        self.object.upload_images()
        success_url = reverse('adv_banners:order', args=[order.pk])

        return HttpResponseRedirect(success_url)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['banner_block'] = self.block
        cleaned_data = getattr(context_data['form'], 'cleaned_data', None)

        if cleaned_data:
            for valid_filter in ['branches', 'country', 'chamber']:
                obj_list = cleaned_data.get(valid_filter, None)

                if obj_list:
                    model_type = ContentType.objects.get_for_model(obj_list[0])
                    prices = AdvertisementPrices.objects.filter(content_type__pk=model_type.pk,
                                                                object_id__in=obj_list,
                                                                advertisement_type='banner',
                                                                dates__contains=now())
                    price_dict = dict((p.object_id, p.price) for p in prices)
                    context_data[valid_filter] =[]

                    for item in obj_list:
                        cost = price_dict.get(item.pk, 0)

                        context_data[valid_filter].append({
                            'name': item.name,
                            'id': item.pk,
                            'cost': cost,
                        })

        return context_data


@login_required
def adv_json_filter(request):
    """
        Getting filters for advertisement
    """
    filter_model = request.GET.get('type', None)
    q = request.GET.get('q', '').strip()

    try:
        page = int(request.GET.get('page', None))
    except ValueError:
        return HttpResponse(json.dumps({'content': [], 'total': 0}))

    if filter_model and (len(q) >= 3 or len(q) == 0):
        obj_list, total = func.autocomplete_filter(filter_model, q, page)

        if total > 0:
            model_type = ContentType.objects.get_for_model(obj_list[0])
            prices = AdvertisementPrices.objects.filter(content_type__pk=model_type.pk,
                                                        object_id__in=obj_list,
                                                        advertisement_type='banner',
                                                        dates__contains=now())
            price_dict = dict((p.object_id, p.price) for p in prices)
            items = []

            for item in obj_list:
                cost = price_dict.get(item.pk, 0)

                result_dict = {
                    'title': item.name,
                    'id': item.pk,
                    'cost': float(cost),
                }

                items.append(result_dict)

            return HttpResponse(json.dumps({'content': items, 'total': total}))

    return HttpResponse(json.dumps({'content': [], 'total': 0}))


class OrderDetail(DetailView):
    model = AdvertisementOrder
    template_name = 'AdvBanner/order.html'
    context_object_name = 'item'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        model_type = ContentType.objects.get_for_model(self.request.user)
        order_filter = Q(content_type__pk=model_type.pk, object_id=self.request.user.pk)
        organization_id = self.request.session.get('current_company', None)

        if organization_id is not None:
            organization = Organization.objects.get(pk=organization_id)
            model_type = ContentType.objects.get_for_model(organization)
            order_filter |= Q(content_type__pk=model_type.pk, object_id=organization.pk)

        return super().get_queryset().filter(order_filter)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['price_components'] = context_data['item'].price_components.all().prefetch_related('item')

        return context_data
