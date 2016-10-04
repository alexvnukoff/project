import json

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _
from django.views.generic import (TemplateView, DetailView, View, CreateView,
                                        UpdateView, DeleteView, RedirectView)

from b24online.AdminTpp.forms import AdvertisementPricesForm, BannerBlockForm
from b24online.models import (User, Branch, Country, B2BProductCategory,
        AdvertisementOrder, Banner, Chamber, AdvertisementPrice, BannerBlock,
        StaticPage, Greeting)
from b24online.search_indexes import SearchEngine, ProfileIndex, GreetingIndex
from b24online.utils import class_for_name
from centerpokupok.models import B2CProductCategory
from core.cbv import JSONResponseMixin


class BaseAdminAuth(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_commando and not request.user.is_superuser:
            return HttpResponseBadRequest()

        return super().dispatch(request, *args, **kwargs)


class BaseAdminTpp(BaseAdminAuth, JSONResponseMixin, TemplateView):
    def render_to_response(self, context, **response_kwargs):
        if self.request.is_ajax():
            return self.render_to_json_response(context)
        else:
            return super().render_to_response(context)


class Dashboard(BaseAdminTpp):
    template_name = "b24online/AdminTpp/dashboard.html"
    valid_models = {
        Branch.__name__.lower(): Branch,
        Country.__name__.lower(): Country,
        B2BProductCategory.__name__.lower(): B2BProductCategory,
        B2CProductCategory.__name__.lower(): B2CProductCategory
    }

    def dispatch(self, request, *args, **kwargs):
        self.model = kwargs.pop('model', None)
        return super().dispatch(request, *args, **kwargs)

    def get_data(self, context):
        if self.model not in self.valid_models:
            return {}

        display_start = int(self.request.GET.get('iDisplayStart', 1))
        display_len = int(self.request.GET.get('iDisplayLength', 10))
        model = self.valid_models[self.model]

        if display_start == 1:
            page = 1
        else:
            page = int(display_start / display_len + 1)

        queryset = model.objects.order_by('name')
        paginator = Paginator(queryset, 10)
        on_page = paginator.page(page)

        return {
            "sEcho": int(self.request.GET.get('sEcho', 1)),
            "iTotalRecords": paginator.count,
            "iTotalDisplayRecords": paginator.count,
            "aaData": [(obj.name, obj.pk) for obj in on_page.object_list]
        }

    def post(self, request, *args, **kwargs):
        if self.model in self.valid_models:
            obj_id = request.POST.get('id', None)
            model = self.valid_models[self.model]
            instance = model.objects.get(pk=obj_id)
            form_class = class_for_name('b24online.AdminTpp.forms', "%sForm" % model.__name__)
            form = form_class(request.POST, instance=instance)

            if form.is_valid():
                form.save()
                return HttpResponse('')

        return HttpResponseBadRequest()


class Users(BaseAdminTpp):
    template_name = "b24online/AdminTpp/users.html"

    def get_data(self, context):
        display_start = int(self.request.GET.get('iDisplayStart', 1))
        display_len = int(self.request.GET.get('iDisplayLength', 10))
        sortCol_0 = int(self.request.GET.get('iSortCol_0', 0))
        sortingCols = int(self.request.GET.get('iSortingCols', 0))
        search = self.request.GET.get('sSearch', "").strip()

        cols = [False, False, 'last_login', 'date_joined', False, False]
        orderby = ['profile__first_name', 'profile__middle_name', 'profile__last_name']

        if sortCol_0 > 0:
            orderby = []

            for x in range(sortingCols):
                param = 'iSortCol_%s' % x
                colIndex = self.request.GET.get(param, -1)
                colIndex = int(colIndex)

                if colIndex != -1 and colIndex in cols and cols[colIndex]:
                    param = 'sSortDir_%s' % x
                    dir = self.request.GET.get(param, 'asc')

                    if dir == 'asc':
                        orderby.append(cols[colIndex])
                    else:
                        orderby.append('-%s' % cols[colIndex])

        if display_start == 1:
            page = 1
        else:
            page = int(display_start / display_len + 1)

        if search:
            s = SearchEngine(doc_type=ProfileIndex)
            s = s.query("multi_match", query=search, fields=['name', 'email'])
            paginator = Paginator(s, 10)
            on_page = paginator.page(page)

            objects = get_user_model().objects.filter(profile__pk__in=[obj.django_id for obj in on_page.object_list.execute().hits]) \
                .prefetch_related('profile')
        else:
            queryset = get_user_model().objects.order_by(*orderby)
            paginator = Paginator(queryset, 10)
            on_page = paginator.page(page)
            objects = on_page.object_list.prefetch_related('profile')

        result_data = []

        for obj in objects:
            profile = getattr(obj, 'profile', None)

            result_data.append([
                profile.full_name if profile else '',
                obj.email,
                obj.last_login.strftime("%Y-%m-%d") if obj.last_login else '',
                obj.date_joined.strftime("%Y-%m-%d") if obj.date_joined else '',
                obj.pk
            ])

        return {
            "sEcho": int(self.request.GET.get('sEcho', 1)),
            "iTotalRecords": paginator.count,
            "iTotalDisplayRecords": paginator.count,
            "aaData": result_data
        }


class Adv(BaseAdminTpp):
    template_name = "b24online/AdminTpp/adv.html"

    def get_data(self, context):
        queryset = AdvertisementOrder.objects.all().order_by('-created_at')

        display_start = int(self.request.GET.get('iDisplayStart', 1))
        display_len = int(self.request.GET.get('iDisplayLength', 10))

        if display_start == 1:
            page = 1
        else:
            page = int(display_start / display_len + 1)

        paginator = Paginator(queryset, 10)
        on_page = paginator.page(page)
        result_data = []

        banner_model_type = ContentType.objects.get_for_model(Banner)

        for obj in on_page.object_list.select_related('content_type', 'advertisement'):
            adv_object = getattr(obj.advertisement, 'banner', None) or getattr(obj.advertisement,
                                                                               'contextadvertisement', None)
            status = 0

            if obj.end_date <= now().date():
                status = 2
            elif adv_object.is_active:
                status = 1

            result_data.append([
                _('Banner') if obj.content_type == banner_model_type else _('Top'),
                obj.purchaser.name,
                reverse('AdminTpp:adv_targets', args=[obj.pk]),
                obj.start_date.strftime("%Y-%m-%d"),
                obj.end_date.strftime("%Y-%m-%d"),
                status,
                float(obj.total_cost),
                obj.pk,
                getattr(obj.advertisement, 'image', None)
            ])

        return {
            'aaData': result_data,
            "sEcho": int(self.request.GET.get('sEcho', 1)),
            "iTotalRecords": paginator.count,
            "iTotalDisplayRecords": paginator.count
        }

    def post(self, request, *args, **kwargs):
        order = get_object_or_404(AdvertisementOrder, pk=request.POST.get('id', None))
        adv_object = getattr(order.advertisement, 'banner', None) or getattr(order.advertisement,
                                                                             'contextadvertisement', None)
        adv_object.is_active = not adv_object.is_active
        adv_object.save()

        return HttpResponse('')


class AdvTargets(BaseAdminAuth, DetailView):
    template_name = 'b24online/AdminTpp/targetsList.html'
    model = AdvertisementOrder

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        adv_object = getattr(self.object.advertisement, 'banner', None) or \
                     getattr(self.object.advertisement, 'contextadvertisement', None)
        context_data['target_list'] = {}

        for target in adv_object.targets.all().prefetch_related('item'):
            context_data['target_list'][target.pk] = {'name': target.item.name, 'price': 0}

        for pricing in self.object.price_components.all().prefetch_related('item'):
            context_data['target_list'][pricing.item.pk]['price'] = pricing.price

        return context_data


class AdvPrice(BaseAdminTpp):
    template_name = "b24online/AdminTpp/prices.html"
    valid_models = {
        Branch.__name__.lower(): Branch,
        Country.__name__.lower(): Country,
        Chamber.__name__.lower(): Chamber,
    }

    def dispatch(self, request, *args, **kwargs):
        self.model = kwargs.pop('model', None)
        return super().dispatch(request, *args, **kwargs)

    def get_data(self, context):
        if self.model not in self.valid_models:
            return {}

        display_start = int(self.request.GET.get('iDisplayStart', 1))
        display_len = int(self.request.GET.get('iDisplayLength', 10))
        search = self.request.GET.get('sSearch', "").strip()
        model = self.valid_models[self.model]

        if display_start == 1:
            page = 1
        else:
            page = int(display_start / display_len + 1)

        if search:
            s = SearchEngine(doc_type=model.get_index_model())
            s = s.query("match", name_auto=search).sort('name_auto')
            paginator = Paginator(s, 10)
            on_page = paginator.page(page)

            objects = model.objects.filter(pk__in=[obj.django_id for obj in on_page.object_list.execute().hits]) \
                .prefetch_related('prices')
        else:
            queryset = model.objects.order_by('name')
            paginator = Paginator(queryset, 10)
            on_page = paginator.page(page)
            objects = on_page.object_list.prefetch_related('prices')

        result_data = []

        for obj in objects:
            result_data.append([
                obj.name,
                float(getattr(obj.prices.last(), 'price', 0)),
                obj.pk
            ])

        return {
            "sEcho": int(self.request.GET.get('sEcho', 1)),
            "iTotalRecords": paginator.count,
            "iTotalDisplayRecords": paginator.count,
            "aaData": result_data
        }

    def post(self, request, *args, **kwargs):
        if self.model in self.valid_models:
            model_type = ContentType.objects.get_for_model(self.valid_models[self.model])
            obj_id = request.POST.get('id', None)

            try:
                adv_price_obj = AdvertisementPrice.objects.get(content_type=model_type, object_id=obj_id)
                adv_price_obj.dates = (adv_price_obj.start_date, now())
                adv_price_obj.updated_by = request.user
                adv_price_obj.save()
            except ObjectDoesNotExist:
                pass

            form = AdvertisementPricesForm(request.POST)

            if form.is_valid():
                form.instance.dates = (now(), None)
                form.instance.content_type = model_type
                form.instance.object_id = obj_id
                form.instance.created_by = request.user
                form.instance.updated_by = request.user
                form.save()

                return HttpResponse('')

        return HttpResponseBadRequest()


class AdvSettings(BaseAdminTpp):
    template_name = "b24online/AdminTpp/adv_sett.html"

    def get_data(self, context):
        display_start = int(self.request.GET.get('iDisplayStart', 1))
        display_len = int(self.request.GET.get('iDisplayLength', 10))

        if display_start == 1:
            page = 1
        else:
            page = int(display_start / display_len + 1)

        queryset = BannerBlock.objects.order_by('name')
        paginator = Paginator(queryset, 10)
        on_page = paginator.page(page)

        result_data = []

        for obj in on_page.object_list:
            result_data.append([
                obj.name,
                obj.get_block_type_display(),
                obj.factor,
                obj.width or '',
                obj.height or '',
                obj.pk
            ])

        return {
            "sEcho": int(self.request.GET.get('sEcho', 1)),
            "iTotalRecords": paginator.count,
            "iTotalDisplayRecords": paginator.count,
            "aaData": result_data
        }

    def post(self, request, *args, **kwargs):
        obj_id = request.POST.get('id')
        block_type = get_object_or_404(BannerBlock, pk=obj_id)
        form = BannerBlockForm(request.POST, instance=block_type)

        if form.is_valid():
            form.save()
            return HttpResponse('')

        return HttpResponseBadRequest()


class StaticPageCreate(BaseAdminAuth, CreateView):
    model = StaticPage
    template_name = "b24online/AdminTpp/pages.html"
    success_url = reverse_lazy('AdminTpp:pages')
    fields = ('title', 'content', 'is_on_top', 'page_type')

    def get_data(self, context):
        display_start = int(self.request.GET.get('iDisplayStart', 1))
        display_len = int(self.request.GET.get('iDisplayLength', 10))

        if display_start == 1:
            page = 1
        else:
            page = int(display_start / display_len + 1)

        queryset = StaticPage.objects.order_by('title')
        paginator = Paginator(queryset, 10)
        on_page = paginator.page(page)

        result_data = []

        for obj in on_page.object_list:
            result_data.append([
                obj.title,
                obj.is_on_top,
                obj.get_page_type_display(),
                [reverse('AdminTpp:pages_edit', args=[obj.pk]), reverse('AdminTpp:pages_delete', args=[obj.pk])]
            ])

        return {
            "sEcho": int(self.request.GET.get('sEcho', 1)),
            "iTotalRecords": paginator.count,
            "iTotalDisplayRecords": paginator.count,
            "aaData": result_data
        }

    def render_to_response(self, context, **response_kwargs):
        if self.request.is_ajax():
            return JsonResponse(self.get_data(context))

        return super().render_to_response(context, **response_kwargs)


class StaticPageUpdate(BaseAdminAuth, UpdateView):
    model = StaticPage
    template_name = "b24online/AdminTpp/pages.html"
    success_url = reverse_lazy('AdminTpp:pages')
    fields = ('title', 'content', 'is_on_top', 'page_type')


class StaticPageDelete(BaseAdminAuth, DeleteView):
    model = StaticPage
    success_url = reverse_lazy('AdminTpp:pages')

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)


class GreetingCreate(BaseAdminAuth, CreateView):
    model = Greeting
    template_name = "b24online/AdminTpp/greetings.html"
    success_url = reverse_lazy('AdminTpp:greetings')
    fields = ('photo', 'name', 'position_name', 'organization_name', 'content')

    def get_data(self, context):
        display_start = int(self.request.GET.get('iDisplayStart', 1))
        display_len = int(self.request.GET.get('iDisplayLength', 10))
        search = self.request.GET.get('sSearch', "").strip()

        if display_start == 1:
            page = 1
        else:
            page = int(display_start / display_len + 1)

        if search:
            s = SearchEngine(doc_type=GreetingIndex)
            s = s.query("multi_match", query=search, fields=['name', 'organization_name'])
            paginator = Paginator(s, 10)
            on_page = paginator.page(page)

            objects = self.model.objects.filter(pk__in=[obj.django_id for obj in on_page.object_list.execute().hits])
        else:
            queryset = self.model.objects.order_by('name')
            paginator = Paginator(queryset, 10)
            on_page = paginator.page(page)
            objects = on_page.object_list

        result_data = []

        for obj in objects:
            result_data.append([
                obj.photo.big,
                obj.name,
                obj.position_name,
                obj.organization_name,
                [reverse('AdminTpp:greetings_edit', args=[obj.pk]), reverse('AdminTpp:greetings_delete', args=[obj.pk])]
            ])

        return {
            "sEcho": int(self.request.GET.get('sEcho', 1)),
            "iTotalRecords": paginator.count,
            "iTotalDisplayRecords": paginator.count,
            "aaData": result_data
        }

    def form_valid(self, form):
        self.object = form.save()
        self.object.upload_images()
        self.object.reindex()

        return super().form_valid(form)

    def render_to_response(self, context, **response_kwargs):
        if self.request.is_ajax():
            return JsonResponse(self.get_data(context))

        return super().render_to_response(context, **response_kwargs)


class GreetingUpdate(BaseAdminAuth, UpdateView):
    model = Greeting
    template_name = "b24online/AdminTpp/greetings.html"
    success_url = reverse_lazy('AdminTpp:greetings')
    fields = ('photo', 'name', 'position_name', 'organization_name', 'content')

    def form_valid(self, form):
        self.object = form.save()

        if 'photo' in form.changed_data:
            self.object.upload_images()
        self.object.reindex()

        return super().form_valid(form)


class GreetingDelete(BaseAdminAuth, DeleteView):
    model = Greeting
    success_url = reverse_lazy('AdminTpp:greetings')

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)


class Activation(BaseAdminTpp):
    template_name = "b24online/AdminTpp/activate.html"

    def get_data(self, context):
        display_start = int(self.request.GET.get('iDisplayStart', 1))
        display_len = int(self.request.GET.get('iDisplayLength', 10))
        sortCol_0 = int(self.request.GET.get('iSortCol_0', 0))
        sortingCols = int(self.request.GET.get('iSortingCols', 0))
        search = self.request.GET.get('sSearch', "").strip()

        cols = ['email', 'last_login', 'date_joined', 'id']
        orderby = ['id']

        if sortCol_0 > 0:
            orderby = []

            for x in range(sortingCols):
                param = 'iSortCol_%s' % x
                colIndex = self.request.GET.get(param, -1)
                colIndex = int(colIndex)

                if colIndex != -1 and colIndex in cols and cols[colIndex]:
                    param = 'sSortDir_%s' % x
                    dir = self.request.GET.get(param, 'asc')

                    if dir == 'asc':
                        orderby.append(cols[colIndex])
                    else:
                        orderby.append('-%s' % cols[colIndex])

        if display_start == 1:
            page = 1
        else:
            page = int(display_start / display_len + 1)

        if search:
            print(search)
            s = User.objects.filter(is_active=False, email__contains=search)
            paginator = Paginator(s, 10)
            on_page = paginator.page(page)
            objects = on_page

        else:
            queryset = User.objects.filter(is_active=False).order_by('id')
            paginator = Paginator(queryset, 10)
            on_page = paginator.page(page)
            objects = on_page

        result_data = []

        for obj in objects:
            #profile = getattr(obj, 'email', None)

            result_data.append([
                obj.email,
                obj.last_login.strftime("%Y-%m-%d") if obj.last_login else '',
                obj.date_joined.strftime("%Y-%m-%d") if obj.date_joined else '',
                obj.pk
            ])

        return {
            "sEcho": int(self.request.GET.get('sEcho', 1)),
            "iTotalRecords": paginator.count,
            "iTotalDisplayRecords": paginator.count,
            "aaData": result_data
        }


class ActivationAction(RedirectView):
    def get(self, request, *args, **kwargs):
        url = self.get_redirect_url(*args, **kwargs)

        if request.user.is_superuser:
            user = get_object_or_404(User, pk=kwargs['pk'])
            user.is_active = True
            user.save()
            return HttpResponseRedirect(url)
        else:
            return HttpResponseBadRequest()

    def get_redirect_url(self, *args, **kwargs):
        url = reverse('AdminTpp:activation')
        return url

