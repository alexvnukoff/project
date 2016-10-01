import json
from decimal import Decimal

from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseNotFound, HttpResponseBadRequest
from django.http import JsonResponse
from django.shortcuts import HttpResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.utils.timezone import now

from django.views.generic import DetailView

from appl import func
from b24online.models import AdvertisementPrice, AdvertisementOrder, ContextAdvertisement, Organization, \
    AdvertisementTarget, Chamber, B2BProduct, BusinessProposal, InnovationProject, Tender, Exhibition, Company, News
from jobs.models import Requirement, Resume
from b24online.AdvTop.forms import ContextAdvertisementForm
from b24online.cbv import ItemCreate


@login_required
def adv_json_filter(request):
    filter_model = request.GET.get('type', None)
    q = request.GET.get('q', '').strip()

    try:
        page = int(request.GET.get('page', None))
    except ValueError:
        return JsonResponse({'content': [], 'total': 0})

    if filter_model and (len(q) >= 3 or len(q) == 0):
        obj_list, total = func.autocomplete_filter(filter_model, q, page)

        if total > 0:
            model_type = ContentType.objects.get_for_model(obj_list[0])
            prices = AdvertisementPrice.objects.filter(content_type__pk=model_type.pk,
                                                        object_id__in=obj_list,
                                                        advertisement_type='context',
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

            return JsonResponse({'content': items, 'total': total})

    return JsonResponse({'content': [], 'total': 0})


class CreateContextAdvertisement(ItemCreate):
    model = ContextAdvertisement
    form_class = ContextAdvertisementForm
    template_name = 'b24online/AdvTop/addForm.html'
    success_url = None
    allowed_types = {
        Chamber.__name__.lower(): Chamber,
        B2BProduct.__name__.lower(): B2BProduct,
        Requirement.__name__.lower(): Requirement,
        BusinessProposal.__name__.lower(): BusinessProposal,
        InnovationProject.__name__.lower(): InnovationProject,
        Tender.__name__.lower(): Tender,
        Exhibition.__name__.lower(): Exhibition,
        Resume.__name__.lower(): Resume,
        News.__name__.lower(): News,
        Company.__name__.lower(): Company
    }

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        class_name = request.GET.get('type', None)
        pk = request.GET.get('id', None)

        if not class_name or not pk:
            return HttpResponseNotFound()

        if class_name not in self.allowed_types:
            return HttpResponseNotFound()

        self.adv_model = self.allowed_types.get(class_name)
        self.adv_item = self.adv_model.objects.get(pk=pk)

        if not self.adv_item.has_perm(request.user):
            return HttpResponseBadRequest()

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        form.instance.site = None
        form.instance.is_active = False
        form.instance.dates = (form.cleaned_data['start_date'], form.cleaned_data['end_date'])
        form.instance.item = self.adv_item

        organization_id = self.request.session.get('current_company', None)
        organization = Organization.objects.get(pk=organization_id)

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

            prices = AdvertisementPrice.objects.filter(price_filter, advertisement_type='context', dates__contains=now())
            days = (form.cleaned_data['end_date'] - form.cleaned_data['start_date']).days
            total_cost = sum([target.price for target in prices]) * Decimal(days)
            order = AdvertisementOrder.objects.create(advertisement=self.object,
                                                      total_cost=total_cost,
                                                      purchaser=organization,
                                                      dates=(form.cleaned_data['start_date'], form.cleaned_data['end_date']),
                                                      created_by=self.request.user,
                                                      updated_by=self.request.user)
            order.price_components.add(*prices)

        success_url = reverse('adv_top:order', args=[order.pk])

        return HttpResponseRedirect(success_url)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['adv_item'] = self.adv_item
        cleaned_data = getattr(context_data['form'], 'cleaned_data', None)

        if cleaned_data:
            for valid_filter in ['branches', 'country', 'chamber']:
                obj_list = cleaned_data.get(valid_filter, None)

                if obj_list:
                    model_type = ContentType.objects.get_for_model(obj_list[0])
                    prices = AdvertisementPrice.objects.filter(content_type__pk=model_type.pk,
                                                                object_id__in=obj_list,
                                                                advertisement_type='context',
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


class OrderDetail(DetailView):
    model = AdvertisementOrder
    template_name = 'b24online/AdvTop/order.html'
    context_object_name = 'item'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.object = AdvertisementOrder.objects.get(pk=kwargs.get('pk'))

        if not self.object.has_perm(request.user):
            return HttpResponseBadRequest()

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        organization_id = self.request.session.get('current_company', None)
        organization = Organization.objects.get(pk=organization_id)
        model_type = ContentType.objects.get_for_model(organization)

        return super().get_queryset().filter(content_type__pk=model_type.pk, object_id=organization.pk)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['price_components'] = context_data['item'].price_components.all().prefetch_related('item')

        return context_data
