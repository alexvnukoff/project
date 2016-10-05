from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse_lazy, reverse
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext as _
from guardian.shortcuts import get_objects_for_user

from appl import func
from b24online.Tpp.forms import AdditionalPageFormSet, ChamberForm
from b24online.cbv import ItemsList, ItemDetail, ItemUpdate, ItemCreate, DeleteGalleryImage, GalleryImageList, \
    DocumentList, DeleteDocument
from b24online.models import (Chamber, Company, News, Tender, Exhibition,
                              BusinessProposal, InnovationProject,
                              Organization, Vacancy, StaffGroup,
                              PermissionsExtraGroup, Country)
from b24online.search_indexes import SearchEngine
from b24online.utils import handle_uploaded_file


class ChamberList(ItemsList):
    # pagination url
    url_paginator = "tpp:paginator"
    url_my_paginator = "tpp:my_main_paginator"
    addUrl = 'tpp:add'

    # Lists of required scripts and styles for ajax request
    styles = [
        settings.STATIC_URL + 'b24online/css/news.css',
        settings.STATIC_URL + 'b24online/css/company.css',
        settings.STATIC_URL + 'b24online/css/tpp.reset.css'
    ]

    current_section = _("Tpp")

    # allowed filter list
    # filter_list = ['country']

    filter_list = {
        'countries': Country
    }

    model = Chamber

    def get_filtered_items(self):
        s = SearchEngine(doc_type=self.model.get_index_model())
        q = self.request.GET.get('q', '').strip()

        for filter_key in list(self.filter_list.keys()):
            filter_lookup = "filter[%s][]" % filter_key
            values = self.request.GET.getlist(filter_lookup)
            print(values)
            if values:
                s = s.filter('terms', **{filter_key: values})

        # Apply geo_country by our internal code
        if (not self.my
            and self.request.session['geo_country']
            and not self.request.GET.get('order1')
            and not self.request.path == '/products/сoupons/'
           ):
            s = s.filter('terms', **{'countries': [self.request.session['geo_country']]})

        if q:
            s = s.query("multi_match", query=q, fields=['title', 'name', 'description', 'content'])

        return self.filter_search_object(s)

    def ajax(self, request, *args, **kwargs):
        self.template_name = 'b24online/Tpp/contentPage.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'b24online/Tpp/index.html'

    def optimize_queryset(self, queryset):
        return queryset.select_related('parent').prefetch_related('countries')

    def get_add_url(self):
        if self.request.user.is_authenticated() and (self.request.user.is_superuser or self.request.user.is_commando):
            return self.addUrl

        return None

    def get_queryset(self):
        queryset = super(ChamberList, self).get_queryset()

        if self.is_my():
            current_org = self._current_organization

            if current_org is not None:
                queryset = self.model.get_active_objects().filter(Q(parent_id=current_org) | Q(pk=current_org))
            else:
                queryset = get_objects_for_user(self.request.user, ['b24online.manage_organization'],
                                                Organization.get_active_objects().all()).instance_of(Chamber)

        return queryset

            #if current_org is not None:
            #    return queryset.filter(pk=current_org)
            #else:
            #    queryset = get_objects_for_user(self.request.user, ['b24online.manage_organization'],
            #                                    Organization.get_active_objects().all()).instance_of(Chamber)

        #return queryset

    def get(self, request, *args, **kwargs):
        for f, model in self.filter_list.items():
            key = "filter[%s][]" % f
            values = request.GET.getlist(key)

            if values:
                self.applied_filters[f] = model.objects.filter(pk__in=values)

        # Apply geo_country by our internal code
        if (not self.my
            and self.request.session['geo_country']
            and not self.request.GET.get('order1')
            and not self.request.path == '/products/сoupons/'
           ):
            geo_country = self.request.session['geo_country']
            self.applied_filters['countries'] = Country.objects.filter(pk=geo_country).only('pk', 'name')

        if request.is_ajax():
            self.ajax(request, *args, **kwargs)
        else:
            self.no_ajax(request, *args, **kwargs)

        return super(ItemsList, self).get(request, *args, **kwargs)


class ChamberDetail(ItemDetail):
    model = Chamber
    template_name = 'b24online/Tpp/detailContent.html'
    addUrl = 'tpp:add'

    current_section = _("Tpp")

    def get_add_url(self):
        if self.request.user.is_authenticated() and (self.request.user.is_superuser or self.request.user.is_commando):
            return self.addUrl
        return None

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data.update({'staffgroups': StaffGroup.get_options()})
        context_data.update({
            'extragroups': PermissionsExtraGroup.get_options()
        })
        return context_data


def _tab_companies(request, tpp, page=1):
    companies = Company.get_active_objects().filter(parent=tpp)
    paginator = Paginator(companies, 10)

    page = paginator.page(page)
    paginator_range = func.get_paginator_range(page)

    url_paginator = "tpp:tab_companies_paged"

    template_params = {
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'url_parameter': tpp
    }

    return render(request, 'b24online/Tpp/tabCompanies.html', template_params)


def _tab_news(request, tpp, page=1):
    news = News.get_active_objects().filter(organization=tpp)
    paginator = Paginator(news, 10)
    page = paginator.page(page)
    paginator_range = func.get_paginator_range(page)

    url_paginator = "tpp:tab_news_paged"

    template_params = {
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'url_parameter': tpp
    }

    return render(request, 'b24online/Tpp/tabNews.html', template_params)


def _tab_tenders(request, tpp, page=1):
    tenders = Tender.objects.filter(organization=tpp)
    paginator = Paginator(tenders, 10)
    page = paginator.page(page)
    paginator_range = func.get_paginator_range(page)

    url_paginator = "tpp:tab_tenders_paged"

    template_arams = {
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'url_parameter': tpp
    }

    return render(request, 'b24online/Tpp/tabTenders.html', template_arams)


def _tab_exhibitions(request, tpp, page=1):
    exhibitions = Exhibition.get_active_objects().filter(organization=tpp)
    paginator = Paginator(exhibitions, 10)
    page = paginator.page(page)
    paginator_range = func.get_paginator_range(page)

    url_paginator = "tpp:tab_exhibitions_paged"

    template_params = {
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'url_parameter': tpp
    }

    return render(request, 'b24online/Tpp/tabExhibitions.html', template_params)


def _tab_proposals(request, tpp, page=1):
    proposals = BusinessProposal.get_active_objects().filter(organization=tpp)
    paginator = Paginator(proposals, 10)
    page = paginator.page(page)
    paginator_range = func.get_paginator_range(page)

    url_paginator = "tpp:tab_proposal_paged"

    template_params = {
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'url_parameter': tpp
    }

    return render(request, 'b24online/Companies/tabProposal.html', template_params)


def _tab_innovation_projects(request, tpp, page=1):
    projects = InnovationProject.get_active_objects().filter(organization=tpp)
    paginator = Paginator(projects, 10)
    page = paginator.page(page)
    paginator_range = func.get_paginator_range(page)

    url_paginator = "tpp:tab_innov_paged"

    template_params = {
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'url_parameter': tpp
    }

    return render(request, 'b24online/Companies/tabInnov.html', template_params)


def _tab_structure(request, tpp, page=1):
    organization = get_object_or_404(Chamber, pk=tpp)

    if request.is_ajax() and not request.user.is_anonymous() and request.user.is_authenticated():
        item_id = request.POST.get("id", None)
        name = request.POST.get('name', '').strip()
        action = request.POST.get("action", None)
        request_type = request.POST.get("type", None)

        if not (request_type in ('department', 'vacancy')) and action is not None:
            return HttpResponseBadRequest()

        if not organization.has_perm(request.user) and action is not None:
            return HttpResponseBadRequest()

        if action == "add" and len(name) > 0:
            if request_type == 'department':
                organization.create_department(name, request.user)
            elif item_id is not None:  # new vacancy
                obj = get_object_or_404(organization.departments, pk=item_id)
                organization.create_vacancy(name, obj, request.user)

        elif action == "edit" and item_id is not None and len(name) > 0:
            if request_type == 'department':
                obj = get_object_or_404(organization.departments, pk=item_id)
            else:
                obj = get_object_or_404(organization.vacancies, pk=item_id)

            obj.name = name
            obj.save()
        elif action == "remove" and item_id is not None:
            if request_type == 'department':
                obj = get_object_or_404(organization.departments, pk=item_id)
            else:
                obj = get_object_or_404(organization.vacancies, pk=item_id)

            obj.delete()

    departments = organization.departments.all().prefetch_related('vacancies').order_by('name')


    template_params = {
        'has_perm': organization.has_perm(request.user),
        'departments': departments,
        'url_parameter': tpp,
        'item_pk': tpp
    }

    return render(request, 'b24online/Tpp/tabStructure.html', template_params)


def _tab_staff(request, tpp, page=1):
    organization = get_object_or_404(Chamber, pk=tpp)

    if request.is_ajax() and not request.user.is_anonymous() and request.user.is_authenticated():
        action = request.POST.get('action', False)
        action = action if action else request.GET.get('action', None)

        if not organization.has_perm(request.user) and action is not None:
            return HttpResponseBadRequest()

        if action == "department":
            departments = [{'name': _("Select department"), "value": ""}]

            for department in organization.departments.all().order_by('name'):
                departments.append({"name": department.name, "value": department.pk})

            return JsonResponse(departments, safe=False)

        elif action == "vacancy":
            department = int(request.GET.get("department", 0))

            if department <= 0:
                return HttpResponseBadRequest()

            vacancies = [{'name': _("Select vacancy"), "value": ""}]

            for department in organization.departments.all():
                for vacancy in department.vacancies.all().order_by('name'):
                    vacancies.append({"name": vacancy.name, "value": vacancy.pk})

            return JsonResponse(vacancies, safe=False)

        elif action == "add":
            user = request.POST.get('user', "").strip()
            department = int(request.POST.get('department', 0))
            vacancy = int(request.POST.get('vacancy', 0))

            if not user or department <= 0 or vacancy <= 0:
                return HttpResponseBadRequest()

            try:
                user = get_user_model().objects.get(email=user, is_active=True)
                vacancy = Vacancy.objects.get(pk=vacancy, department__organization=organization)
            except ObjectDoesNotExist:
                return HttpResponseBadRequest(_('User not found'))

            # One user for vacancy
            if vacancy.user:
                return HttpResponseBadRequest(_("The vacancy already have employee attached"))

            if user.work_positions.filter(department__organization=organization).exists():
                return HttpResponseBadRequest(_("The user already employed in your organization"))

            admin = bool(int(request.POST.get('admin', 0)))
            vacancy.assign_employee(user, admin)

        elif action == "remove":
            cabinet = int(request.POST.get('id', 0))

            if cabinet > 0:
                user = get_object_or_404(get_user_model(), pk=cabinet)
                vacancy = get_object_or_404(Vacancy, user=user, department__organization=organization)
                vacancy.remove_employee()

    users = get_user_model().objects.filter(is_active=True, work_positions__department__organization=organization).distinct() \
        .select_related('profile').prefetch_related('work_positions', 'work_positions__department')

    paginator = Paginator(users, 10)
    page = paginator.page(page)
    paginator_range = func.get_paginator_range(page)

    url_paginator = "tpp:tab_staff_paged"

    template_params = {
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,
        'url_parameter': tpp,
        'item_pk': tpp,
        'organization': organization,
        'has_perm': organization.has_perm(request.user)
    }

    return render(request, 'b24online/Tpp/tabStaff.html', template_params)


class ChamberGalleryImageList(GalleryImageList):
    owner_model = Chamber
    namespace = 'tpp'


class DeleteChamberGalleryImage(DeleteGalleryImage):
    owner_model = Chamber


class ChamberDocumentList(DocumentList):
    owner_model = Chamber
    namespace = 'tpp'


class DeleteChamberDocument(DeleteDocument):
    owner_model = Chamber


class ChamberUpdate(ItemUpdate):
    model = Chamber
    form_class = ChamberForm
    template_name = 'b24online/Tpp/addForm.html'
    success_url = reverse_lazy('tpp:main')

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

        return context_data

    def form_valid(self, form, additional_page_form):
        """
        Called if all forms are valid. Creates a Recipe instance along with
        associated Ingredients and Instructions and then redirects to a
        success page.
        """
        form.instance.updated_by = self.request.user

        if form.changed_data:
            if 'vatin' in form.changed_data:
                form.instance.metadata['vat_identification_number'] = form.cleaned_data['vatin']

            if 'phone' in form.changed_data:
                form.instance.metadata['phone'] = form.cleaned_data['phone']

            if 'fax' in form.changed_data:
                form.instance.metadata['fax'] = form.cleaned_data['fax']

            if 'email' in form.changed_data:
                form.instance.metadata['email'] = form.cleaned_data['email']

            if 'site' in form.changed_data:
                form.instance.metadata['site'] = form.cleaned_data['site']

            if 'longitude' in form.changed_data or 'latitude' in form.changed_data:
                form.instance.metadata['location'] = '%s,%s' % (form.cleaned_data['latitude'], form.cleaned_data['longitude']),

            if 'flag' in form.changed_data:
                flag = form.cleaned_data.get('flag')
                form.instance.metadata['flag'] = handle_uploaded_file(flag) if flag else None

        form.instance.org_type = 'international' if len(form.cleaned_data.get('countries')) > 1 else 'national'

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
            self.object.upload_images(form.changed_data)

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, additional_page_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """

        return self.render_to_response(self.get_context_data(form=form, additional_page_form=additional_page_form))


class ChamberCreate(ItemCreate):
    org_required = False
    model = Chamber
    form_class = ChamberForm
    template_name = 'b24online/Tpp/addForm.html'
    success_url = reverse_lazy('tpp:main')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated() or not (request.user.is_commando or request.user.is_superuser):
            return HttpResponseRedirect(reverse('denied'))

        return super().dispatch(request, *args, **kwargs)

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
        flag = form.cleaned_data.get('flag')

        form.instance.metadata = {
            'vat_identification_number': form.cleaned_data['vatin'],
            'phone': form.cleaned_data['phone'],
            'fax': form.cleaned_data['fax'],
            'email': form.cleaned_data['email'],
            'site': form.cleaned_data['site'],
            'location': '%s,%s' % (form.cleaned_data['latitude'], form.cleaned_data['longitude']),
            'flag': handle_uploaded_file(flag) if flag else None
        }

        form.instance.org_type = 'international' if len(form.cleaned_data.get('countries')) > 1 else 'national'

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
        return self.render_to_response(context_data)
